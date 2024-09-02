from src.model import Model
from src.workbook import Workbook


if __name__ == "__main__":
    model = Model()
    #model.build_model()
    model.load_model("testModel")
    res1 = model.predict(["Steelers", "Browns"])
    res2 = model.predict(["Vikings", "Lions"])

    print(res1)
    print(res2)
