import numpy as np
import yaml
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials


class Workbook:
    def __init__(self):
        self.data = None
        self.matchups = None
        self.team_stats = None
        with open('../config/config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            scope = [config['sheetScope']]
            credentials = ServiceAccountCredentials.from_json_keyfile_name(config['filePrefix'] + config['credentialsFile'], scope)
            gc = gspread.authorize(credentials)
            spreadsheet_key = config['spreadsheetKey']
            self.__workbook = gc.open_by_key(spreadsheet_key)
            ratings_sheet = self.__workbook.get_worksheet_by_id(0)
            data = ratings_sheet.get_all_values()
            headers = data.pop(0)
            self.__ratings_frame = pd.DataFrame(data, columns=headers)
            self.__ratings_frame.drop(['Home Record', 'Home Wins', 'Home Losses', 'Away Record', 'Away Wins', 'Away Losses', 'Wins', 'Losses'], axis=1, inplace=True)
            self.__ratings_frame['Team'].replace('', np.NAN, inplace=True)
            self.__ratings_frame.dropna(subset=['Team'], inplace=True)

    def get_team_stats(self):
        team_names = self.__ratings_frame['Team'].tolist()[0:32]
        stat_frame = self.__ratings_frame.drop(columns=['Team'], axis=1)
        stat_frame = stat_frame.apply(pd.to_numeric, errors='coerce')
        for col in stat_frame.columns:
            stat_frame[col] = (stat_frame[col] - stat_frame[col].min()) / (stat_frame[col].max() - stat_frame[col].min())
        self.team_stats = {}
        for i in range(32):
            self.team_stats[team_names[i]] = list(stat_frame.iloc[i].tolist())

    def get_winners_losers(self):
        sheet = self.__workbook.get_worksheet_by_id(2059466430)
        data = sheet.get_all_values()
        headers = data.pop(0)
        matchups_frame = pd.DataFrame(data, columns=headers)
        winners = []
        losers = []
        for i in range(len(matchups_frame)):
            winners.append(matchups_frame.iloc[i][1])
            losers.append(matchups_frame.iloc[i][4])
            winners = list(filter(None, winners))
            losers = list(filter(None, losers))
        self.matchups = [list(matchups) for matchups in zip(winners, losers)][1:]
        print(self.matchups)

    def normalize_matchup(self, team1, team2):
        if self.team_stats is None:
            self.get_team_stats()
        match = zip(self.team_stats[team1], self.team_stats[team2])
        result = []
        for iter1, iter2 in match:
            result.append(iter1 - iter2)
        return result

    def build_final_data(self):
        all_matchups = []
        second = False
        if self.matchups is None:
            self.get_winners_losers()
        for match in self.matchups:
            if second:
                matchup = self.normalize_matchup(match[0], match[1])
                matchup.append(1)
                all_matchups.append(matchup)
                second = False
            else:
                matchup = self.normalize_matchup(match[1], match[0])
                matchup.append(0)
                all_matchups.append(matchup)
                second = True
        self.data = pd.DataFrame(all_matchups)
        return self.data
