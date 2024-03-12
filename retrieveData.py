from ftplib import FTP
import pandas as pd
from createPlots import createProdPlot, createEtaPlot, createCSTPlot
from createGauges import createEtaGauge, createPowerGauge, createVar2Gauge, createVar3Gauge
from num2string import convertNumber as cvN
import numpy as np
import csv
import json


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

        Av24 = (str(round(100 * np.mean([last24Data["Availability Inv 1"][0], last24Data["Availability Inv 2"][0]]), 1))
                + " %")
        AvthisMonth = str(round(100 * np.mean([thisMonthData["Availability Inv 1"][0],
                                               thisMonthData["Availability Inv 2"][0]]), 1)) + " %"
        AvthisYear = str(round(100 * np.mean([thisYearData["Availability Inv 1"][0],
                                              thisYearData["Availability Inv 2"][0]]), 1)) + " %"
    else:
        Av24 = str(round(100 * last24Data["Availability"][0], 1)) + " %"
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

        lastVar2 = float('NaN')
        lastVar3 = float('NaN')

    else:
        if Data["PlantType"] == "PV":

            lastVar2 = Data["last24hTL"]["I"].iloc[-1]
            lastVar3 = Data["last24hTL"]["TMod"].iloc[-1]

        else:

            lastVar2 = Data["last24hTL"]["Q"].iloc[-1]
            lastVar3 = Data["last24hTL"]["Bar"].iloc[-1]

    if np.isnan(lastVar2):
        lastVar2 = 0
        
    dataIn = Data["DatiGauge"]
    EtaData = dataIn["Eta"]
    # EtaData["Plant"] = Data["Plant"]
    EtaData["etaName"] = Data["etaName"]

    EtaGaugeData = createEtaGauge(EtaData)

    # dataGauge = {"lastP": lastP, "lastVar3": lastVar3, "lastVar2": lastVar2, "DatiRef": EtaGaugeData["DatiRef"],
    #              "Plant": Data["Plant"], "etaName": Data["etaName"], "PMax": Data["PMax"], "PN": Data["PN"]}

    PowerData = dataIn["Power"]
    PowerGaugeData = createPowerGauge(PowerData)

    if Data["Plant"] != "TF" and Data["Plant"] != "SA3" and Data["Plant"] != "SCN":
        DataQ = lastVar2 * 1000
    else:
        DataQ = lastVar2

    dataGauge = {
        "lastVar2": DataQ, "Var2Max": Data["Var2"]["Max"], "udm": Data["Var2"]["udm"], "Var2name": Data["Var2"]["name"],
        "MeanVar2": Data["Var2"]["Media"], "DevVar2": Data["Var2"]["Dev"], "Plant": Data["Plant"]
    }

    Var2GaugeData = createVar2Gauge(dataGauge)

    dataGauge = {"lastVar3": lastVar3, "Var3Max": Data["Var3"]["Max"], "udm": Data["Var3"]["udm"],
                 "Var3name": Data["Var3"]["name"], "MeanVar3": Data["Var3"]["Media"], "DevVar3": Data["Var3"]["Dev"],
                 "Plant": Data["Plant"]}

    Var3GaugeData = createVar3Gauge(dataGauge)

    GaugeData = {"Eta": EtaGaugeData, "Var2": Var2GaugeData, "Power": PowerGaugeData, "Var3": Var3GaugeData}

    return GaugeData


def createPlots(Data):

    Plant = Data["Plant"]
    dfYearTL = Data["thisYearTL"]
    PlantType = Data["PlantType"]

    if Plant != "TF" and PlantType == "Hydro":
        dfYearTL["Q"] = dfYearTL["Q"] * 1000

    if Plant != "CST":
        dataPlot = {"Plant": Plant, "Timeline": dfYearTL, "Plant state": Data["Plant state"],
                    "Plant type": Data["PlantType"], "PMax": Data["PMax"], "Var2Max": Data["Var2"]["Max"],
                    "Var2udm": Data["Var2"]["udm"]}
        ProductionPlot = createProdPlot(dataPlot)
        
    else:
        dataPlot = {"Plant": Plant, "Timeline": dfYearTL, "Plant state": Data["Plant state"],
                    "Plant type": Data["PlantType"], "PMax": Data["PMax"], "Var2Max": Data["Var2"]["Max"]}
        ProductionPlot = createCSTPlot(dataPlot)

    EtaPlot = createEtaPlot(dataPlot)

    Plots = {"Production plot": ProductionPlot, "Eta plot": EtaPlot}

    return Plots


def readPlantData(Plant):

    ftp = FTP("192.168.10.211", timeout=120)
    ftp.login('ftpdaticentzilio', 'Sd2PqAS.We8zBK')
    udmVar2 = ""

    if Plant == "ST":
        ftp.cwd('/dati/San_Teodoro')
        PlantType = "Hydro"
        PMax = 260
        Var2Max = 80
        Var2Media = 69.4
        Var2Dev = 15
        Var3Media = 27.1
        Var3Dev = 0.5
        Var3Max = 40
        PN = PMax
        udmVar2 = "l/s"
        folder = "San_Teodoro"

    elif Plant == "TF":
        ftp.cwd('/dati/Torrino_Foresta')
        PlantType = "Hydro"
        PMax = 400
        Var2Max = 3
        Var2Media = 0.9787
        Var2Dev = 0.983
        Var3Media = 1.41
        Var3Dev = 0.04
        Var3Max = 2
        PN = PMax
        udmVar2 = "m\u00b3/s"
        folder = "Torrino_Foresta"

    elif Plant == "PG":
        ftp.cwd('/dati/ponte_giurino')
        PlantType = "Hydro"
        Var2Max = 80
        Var2Media = 12
        Var2Dev = 15
        Var3Media = 31.5
        Var3Dev = 0.9
        PMax = 250
        Var3Max = 50
        PN = PMax
        udmVar2 = "l/s"
        folder = "ponte_giurino"

    elif Plant == "SA3":
        
        ftp.cwd('/dati/SA3')
        PlantType = "Hydro"
        Var2Max = 80
        Var2Media = 9.77
        Var2Dev = 9.76
        PMax = 250
        Var3Media = 1.5
        Var3Max = 3
        Var3Dev = 1
        PN = PMax
        udmVar2 = "m\u00b3/s"
        folder = "SA3"

    elif Plant == "CST":

        ftp.cwd('/dati/San_Teodoro')
        PlantType = "Hydro"
        PMax = 260 + 100
        Var2Max = 110
        Var2Media = 26 + 69.4
        Var2Dev = np.sqrt(15 ** 2 + 15 ** 2)
        Var3Media = (27.1 + 26.9) / 2
        Var3Dev = 0.5 * np.sqrt(0.5 ** 2 + 0.5 ** 2)
        Var3Max = 36
        PN = PMax
        udmVar2 = "l/s"
        folder = "San_Teodoro"

    elif Plant == "SCN":

        ftp.cwd('/dati/SCN')
        PlantType = "PV"
        PMax = 930
        Var2Max = 1000
        Var2Media = 390
        Var2Dev = 333
        Var3Media = 27
        Var3Dev = 14
        Var3Max = 70
        PN = 927
        folder = "SCN"

    elif Plant == "RUB":
        ftp.cwd('/dati/Rubino')
        PlantType = "PV"
        PMax = 998
        Var2Max = 1300
        Var2Media = 469
        Var2Dev = 327
        Var3Max = 1300
        Var3Media = 19
        Var3Dev = 16
        PN = 997
        folder = "Rubino"

    else:
        ftp.cwd('/dati/San_Teodoro')
        PlantType = "Hydro"
        PMax = 100
        Var2Max = 30
        Var2Media = 26
        Var2Dev = 6
        Var3Media = 26.9
        Var3Dev = 0.5
        Var3Max = 36
        PN = PMax
        udmVar2 = "l/s"
        folder = "San_Teodoro"

    if PlantType == "Hydro":

        nameVar2 = "Q"
        udmVar3 = "barg"
        nameVar3 = "h"
        etaName = "\u03b7"
    else:
        udmVar2 = "W/m\u00b2"
        nameVar2 = "I"
        udmVar3 = "°C"
        nameVar3 = "T"
        etaName = "PR"

    last24File = Plant + "last24hTL.csv"

    gFile = open(last24File, "wb")
    ftp.retrbinary("RETR " + last24File, gFile.write)
    gFile.close()
    df24hTL = pd.read_csv(last24File)

    df24hTL["PMax"] = PMax
    df24hTL["Var2Max"] = Var2Max
    df24hTL["Var3Max"] = Var3Max

    thisYearFile = Plant + "YearTL.csv"

    gFile = open(thisYearFile, "wb")
    ftp.retrbinary("RETR " + thisYearFile, gFile.write)
    gFile.close()
    thisYearTL = pd.read_csv(thisYearFile)

    thisYearTL["PMax"] = PMax
    thisYearTL["Var2Max"] = Var2Max
    thisYearTL["Var3Max"] = Var3Max

    last24StatFile = Plant + "last24hStat.csv"

    gFile = open(last24StatFile, "wb")
    ftp.retrbinary("RETR " + last24StatFile, gFile.write)
    gFile.close()
    last24Stat = pd.read_csv(last24StatFile)

    last24Stat["PMax"] = PMax
    last24Stat["Var2Max"] = Var2Max
    last24Stat["Var3Max"] = Var3Max

    thisMonthStatFile = Plant + "MonthStat.csv"

    gFile = open(thisMonthStatFile, "wb")
    ftp.retrbinary("RETR " + thisMonthStatFile, gFile.write)
    gFile.close()
    thisMonthStat = pd.read_csv(thisMonthStatFile)

    thisMonthStat["PMax"] = PMax
    thisMonthStat["Var2Max"] = Var2Max
    thisMonthStat["Var3Max"] = Var3Max

    thisYearStatFile = Plant + "YearStat.csv"

    gFile = open(thisYearStatFile, "wb")
    ftp.retrbinary("RETR " + thisYearStatFile, gFile.write)
    gFile.close()
    thisYearStat = pd.read_csv(thisYearStatFile)

    thisYearStat["PMax"] = PMax
    thisYearStat["Var2Max"] = Var2Max
    thisYearStat["Var3Max"] = Var3Max

    # ftp = FTP("192.168.10.211", timeout=120)
    # ftp.login('ftpdaticentzilio', 'Sd2PqAS.We8zBK')
    ftp.cwd('/dati/'+folder)
    gFile = open("dati gauge.csv", "wb")
    ftp.retrbinary('RETR dati gauge.csv', gFile.write)
    gFile.close()

    DatiGauge = pd.read_csv('dati gauge.csv')

    ftp.close()

    Data = {
        "last24hTL": df24hTL, "thisYearTL": thisYearTL, "last24hStat": last24Stat, "thisMonthStat": thisMonthStat,
        "thisYearStat": thisYearStat, "PlantType": PlantType, "PMax": PMax,
        "Var2": {"Max": Var2Max, "udm": udmVar2, "name": nameVar2, "Media": Var2Media, "Dev": Var2Dev},
        "Var3": {"Max": Var3Max, "Media": Var3Media, "Dev": Var3Dev, "udm": udmVar3, "name": nameVar3},
        "etaName": etaName, "PN": PN, "DatiGauge": DatiGauge,
    }

    return Data
