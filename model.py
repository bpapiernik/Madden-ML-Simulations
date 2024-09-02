import pandas as pd
from keras.callbacks import ReduceLROnPlateau, EarlyStopping
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
import keras.regularizers
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from src.workbook import Workbook


class Model:
    def __init__(self):
        self.__wb = Workbook()
        self.__data = self.__wb.build_final_data()
    def build_model(self):
        print(self.__data.columns)
        X = self.__data.iloc[:, 0:21]
        Y = self.__data.iloc[:, 21]
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.05)
        selector = SelectKBest(f_classif, k=6)
        selector.fit(X, Y)
        selected_features = selector.transform(X_train)
        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                                      patience=10, min_lr=0.00001)

        # src: https://keras.io/api/callbacks/early_stopping/
        # stop training if val_loss don't improve within 15 epoch.
        early_stop = EarlyStopping(monitor='val_loss', patience=25)
        model = Sequential()
        model.add(Dense(80, input_dim=6, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001)))
        model.add(Dropout(0.4))
        model.add(Dense(80, kernel_regularizer=keras.regularizers.l2(0.001), activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(1, activation='sigmoid'))
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        model.fit(selected_features, y_train, epochs=950, batch_size=32, validation_split=0.05, callbacks=[reduce_lr, early_stop])
        selected_features = selector.fit_transform(X_test, y_test)
        predictions = model.evaluate(selected_features, y_test)
        print(predictions)
        model.save("testModel")
    def load_model(self, name):
        self.model = keras.models.load_model(name)

    def predict(self, teams):
        stat = self.__wb.normalize_matchup(teams[0], teams[1])
        X = self.__data.iloc[:, 0:21]
        Y = self.__data.iloc[:, 21]
        selector = SelectKBest(f_classif, k=6)
        selector.fit(X, Y)
        stat = selector.transform([stat])

        return self.model.predict(stat)

