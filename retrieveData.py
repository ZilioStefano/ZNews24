from ftplib import FTP
import pandas as pd
from createPlots import createProdPlot, createEtaPlot, createCSTPlot
from createGauges import createEtaGauge, createPowerGauge, createVar2Gauge
from num2string import convertNumber as cvN
import numpy as np


def createLabel(Data):

    last24Data = Data["last24hStat"]
    Elast24, dummy = cvN(last24Data["Energy"][0], "Energy", "HTML", Data["Plant"])

    if np.isnan(last24Data["etaMean"][0]):
        Etalast24 = ""
    else:
        Etalast24 = str(round(100 * last24Data["etaMean"][0], 1)) + " %"

    thisMonthData = Data["thisMonthStat"]
    thisYearData = Data["thisYearStat"]
    Plant = Data["Plant"]

    if Plant == "SCN":

        Av24 = str(round(100 * np.mean([last24Data["Availability Inv 1"][0], last24Data["Availability Inv 2"][0]]),1)) + " %"
        AvthisMonth = str(round(100 * np.mean([thisMonthData["Availability Inv 1"][0], thisMonthData["Availability Inv 2"][0]]), 1)) + " %"
        AvthisYear = str(round(100 * np.mean([thisYearData["Availability Inv 1"][0], thisYearData["Availability Inv 2"][0]]), 1)) + " %"
    else:
        Av24 = str(round(100 * last24Data["Availability"][0],1)) + " %"
        AvthisMonth = str(round(100 * thisMonthData["Availability"][0], 1)) + " %"
        AvthisYear = str(round(100 * thisYearData["Availability"][0], 1)) + " %"

    Yealdlast24, dummy = cvN(last24Data["Resa"][0], "Money", "HTML", Data["Plant"])

    EthisMonth, dummy = cvN(thisMonthData["Energy"][0], "Energy", "HTML", Data["Plant"])
    EtathisMonth = str(round(100 * thisMonthData["etaMean"][0], 1)) + " %"
    YeldthisMonth, dummy = cvN(thisMonthData["Resa"][0], "Money", "HTML", Data["Plant"])

    EthisYear, dummy = cvN(thisYearData["Energy"][0], "Energy", "HTML", Data["Plant"])
    EtathisYear = str(round(100 * thisYearData["etaMean"][0], 1)) + " %"
    YeldthisYear, dummy = cvN(thisYearData["Resa"][0], "Money", "HTML", Data["Plant"])

    if Plant == "SCN" or Plant == "RUB":
        Yealdlast24 = Yealdlast24 + " RID"
        YeldthisMonth = YeldthisMonth + " RID"
        YeldthisYear = YeldthisYear + " RID"

    Label = {"last24h": {"Energy": Elast24, "Eta": Etalast24, "Av": Av24, "Yeald": Yealdlast24},
             "thisMonth": {"Energy": EthisMonth, "Eta": EtathisMonth, "Av": AvthisMonth, "Yeald": YeldthisMonth},
             "thisYear": {"Energy": EthisYear, "Eta": EtathisYear, "Av": AvthisYear, "Yeald": YeldthisYear}}

    return Label


def createGauges(Data):

    if len(Data["last24hTL"]) == 0:
        lastQ = float('NaN')
        lastEta = float('NaN')
        lastP = float('NaN')
        lastVar3 = float('NaN')

    else:
        if Data["PlantType"] == "PV":
            lastQ = Data["last24hTL"]["I"].iloc[-1]
            lastVar3 = Data["last24hTL"]["TMod"].iloc[-1]

        else:
            lastQ = Data["last24hTL"]["Q"].iloc[-1]
            lastVar3 = Data["last24hTL"]["Bar"].iloc[-1]

        lastEta = Data["last24hTL"]["Eta"].iloc[-1]
        lastP = Data["last24hTL"]["P"].iloc[-1]

    if np.isnan(lastEta):
        lastEta = 0

    if np.isnan(lastQ):
        lastQ = 0

    dataGauge = {"lastQ": lastQ, "lastEta": lastEta,
                 "Plant": Data["Plant"], "lastVar3": lastVar3}

    EtaGaugeData = createEtaGauge(dataGauge)

    dataGauge = {"lastP": lastP, "last pressure": lastVar3,
                 "lastQ": lastQ, "DatiRef": EtaGaugeData["DatiRef"], "Plant": Data["Plant"],
                 "PMax": Data["PMax"]}

    PowerGaugeData = createPowerGauge(dataGauge)

    if Data["Plant"] != "TF" and Data["Plant"] != "SA3":
        DataQ = lastQ * 1000
    else:
        DataQ = lastQ

    dataGauge = {"lastVar2": DataQ, "Var2Max": Data["Var2Max"], "udm": Data["Var2udm"],
                 "MeanQ": Data["QMedia"], "DevQ": Data["QDev"], "Plant": Data["Plant"]}
    Var2GaugeData = createVar2Gauge(dataGauge)

    GaugeData = {"Eta": EtaGaugeData, "Var2": Var2GaugeData, "Power": PowerGaugeData}

    return GaugeData


def createPlots(Data):

    Plant = Data["Plant"]
    dfYearTL = Data["thisYearTL"]
    PlantType = Data["PlantType"]

    if Plant != "TF" and PlantType == "Hydro":
        dfYearTL["Q"] = dfYearTL["Q"] * 1000

    if Plant != "CST":
        dataPlot = {"Plant": Plant, "Timeline": dfYearTL, "Plant state": Data["Plant state"],
                    "Plant type": Data["PlantType"], "PMax": Data["PMax"], "Var2Max": Data["Var2Max"]}
        ProductionPlot = createProdPlot(dataPlot)
        
    else:
        dataPlot = {"Plant": Plant, "Timeline": dfYearTL, "Plant state": Data["Plant state"],
                    "Plant type": Data["PlantType"], "PMax": Data["PMax"], "Var2Max": Data["Var2Max"]}
        ProductionPlot = createCSTPlot(dataPlot)

    EtaPlot = createEtaPlot(dataPlot)

    Plots = {"Production plot": ProductionPlot, "Eta plot": EtaPlot}

    return Plots


def readPlantData(Plant):

    ftp = FTP("192.168.10.211", timeout=120)
    ftp.login('ftpdaticentzilio', 'Sd2PqAS.We8zBK')

    if Plant == "ST":
        ftp.cwd('/dati/San_Teodoro')
        PlantType = "Hydro"
        PMax = 259.30
        Var2Max = 80
        QMedia = 66.8
        QDev = 14.4
        udm = " l/s"
        PlantTye = "Hydro"

    elif Plant == "TF":
        ftp.cwd('/dati/Torrino_Foresta')
        PlantType = "Hydro"
        PMax = 400
        Var2Max = 3
        QMedia = 1.94
        QDev = 0.09
        udm = "m\u00b3/s"
        PlantTye = "Hydro"

    elif Plant == "PG":
        ftp.cwd('/dati/ponte_giurino')
        PlantType = "Hydro"
        Var2Max = 80
        QMedia = 9.77
        QDev = 9.76
        PMax = 250
        udm = " l/s"
        PlantTye = "Hydro"

    elif Plant == "SA3":
        ftp.cwd('/dati/SA3')
        PlantType = "Hydro"
        Var2Max = 80
        QMedia = 9.77
        QDev = 9.76
        PMax = 250
        udm = " l/s"
        PlantTye = "Hydro"

    elif Plant == "CST":
        ftp.cwd('/dati/San_Teodoro')
        PlantType = "Hydro"
        PMax = 259.30 + 100
        Var2Max = 110
        QMedia = 22.4 + 66.8
        QDev = np.sqrt(7.8**2 + 14.4**2)
        udm = " l/s"
        PlantTye = "Hydro"
    elif Plant == "SCN":
        ftp.cwd('/dati/SCN')
        PlantType = "PV"
        PMax = 926.64
        Var2Max = 1000
        QMedia = 800
        QDev = 200
        udm = " W/m\u00b2"

    elif Plant == "RUB":
        ftp.cwd('/dati/Rubino')
        PlantType = "PV"
        PMax = 997
        Var2Max = 1000
        QMedia = 800
        QDev = 200
        udm = " W/m\u00b2"

    else:
        ftp.cwd('/dati/San_Teodoro')
        PlantType = "Hydro"
        PMax = 100
        Var2Max = 30
        QMedia = 22.4
        QDev = 7.8
        udm = " l/s"
        PlantTye = "Hydro"

    last24File = Plant + "last24hTL.csv"

    gFile = open(last24File, "wb")
    ftp.retrbinary("RETR " + last24File, gFile.write)
    gFile.close()
    df24hTL = pd.read_csv(last24File)

    df24hTL["PMax"] = PMax
    df24hTL["Var2Max"] = Var2Max

    thisYearFile = Plant + "YearTL.csv"

    gFile = open(thisYearFile, "wb")
    ftp.retrbinary("RETR " + thisYearFile, gFile.write)
    gFile.close()
    thisYearTL = pd.read_csv(thisYearFile)

    thisYearTL["PMax"] = PMax
    thisYearTL["Var2Max"] = Var2Max

    last24StatFile = Plant + "last24hStat.csv"

    gFile = open(last24StatFile, "wb")
    ftp.retrbinary("RETR " + last24StatFile, gFile.write)
    gFile.close()
    last24Stat = pd.read_csv(last24StatFile)

    last24Stat["PMax"] = PMax
    last24Stat["Var2Max"] = Var2Max

    last24File = Plant + "last24hTL.csv"

    thisMonthStatFile = Plant + "MonthStat.csv"

    gFile = open(thisMonthStatFile, "wb")
    ftp.retrbinary("RETR " + thisMonthStatFile, gFile.write)
    gFile.close()
    thisMonthStat = pd.read_csv(thisMonthStatFile)

    thisMonthStat["PMax"] = PMax
    thisMonthStat["Var2Max"] = Var2Max

    thisYearStatFile = Plant + "YearStat.csv"

    gFile = open(thisYearStatFile, "wb")
    ftp.retrbinary("RETR " + thisYearStatFile, gFile.write)
    gFile.close()
    thisYearStat = pd.read_csv(thisYearStatFile)

    thisYearStat["PMax"] = PMax
    thisYearStat["Var2Max"] = Var2Max

    ftp.close()

    Data = {
            "last24hTL": df24hTL, "thisYearTL": thisYearTL, "last24hStat": last24Stat, "thisMonthStat": thisMonthStat,
            "thisYearStat": thisYearStat, "PlantType": PlantType, "PMax": PMax, "Var2Max": Var2Max, "Var2udm": udm,
            "QMedia": QMedia, "QDev": QDev
            }

    if Plant == "CST":
        B = 2

    return Data
