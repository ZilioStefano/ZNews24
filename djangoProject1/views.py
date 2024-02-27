import pandas as pd
from django.shortcuts import render
from ftplib import FTP
import csv
from retrieveData import readPlantData, createPlots, createGauges, createLabel


def readAlarm(Plant):

    ftp = FTP("192.168.10.211", timeout=120)
    ftp.login('ftpdaticentzilio', 'Sd2PqAS.We8zBK')
    ftp.cwd('/dati/Database_Produzione')
    gFile = open("AlarmStatesBeta.csv", "wb")
    ftp.retrbinary('RETR AlarmStatesBeta.csv', gFile.write)
    gFile.close()
    # StatoAllarmi = pd.read_csv("AlarmStatesBeta.csv", on_bad_lines='skip', header='infer', delimiter=';')

    StatoAllarmi = csv.DictReader(open("AlarmStatesBeta.csv"))

    for row in StatoAllarmi:
        StatoAllarmi = row
    if Plant == "SCN":
        CurrAlarm = {"SCN1": StatoAllarmi["SCN1"], "SCN2": StatoAllarmi["SCN2"]}

    else:
        CurrAlarm = StatoAllarmi[Plant]

    return CurrAlarm


def retrieveData(Plant, PlantState):

    Data = readPlantData(Plant)
    Data["Plant state"] = PlantState
    Data["Plant"] = Plant

    Plots = createPlots(Data)
    Gauges = createGauges(Data)
    Label = createLabel(Data)

    if PlantState == "A":
        pageColor = "IndianRed"
    else:
        pageColor = "#e2f5ef"

    HTMLData = {
        "Production": Plots["Production plot"]["Graph"], "Eta": Plots["Eta plot"]["Graph"],
        "GaugeEta": Gauges["Eta"]["HTML"], "LedEta": Gauges["Eta"]["ledColor"], "GaugePower": Gauges["Power"]["HTML"],
        "LedPower": Gauges["Power"]["ledColor"], "Gauge2": Gauges["Var2"]["HTML"], "Led2": Gauges["Var2"]["ledColor"],
        "Gauge3": Gauges["Var3"]["HTML"], "Led3": Gauges["Var3"]["ledColor"],
        "Label": Label, "pagecolor": pageColor
    }

    return HTMLData


def switchPlant():

    Plants = ["SA3", "TF", "ST", "PAR", "CST", "PG", "SCN", "RUB"]
    N = len(Plants)

    indexDf = pd.read_csv('current index.csv')
    indexDf["index"] = (indexDf['index'][0] + 1) % N
    indexDf.to_csv("current index.csv", index=False)
    currPlant = Plants[indexDf["index"][0]]

    return currPlant


def setTemplate(Plant):

    if (Plant == "TF" or Plant == "ST" or Plant == "PAR" or Plant == "SA3" or Plant == "PG" or Plant == "CST"
            or Plant == "SCN" or Plant == "RUB"):
        Template = "mainPage.html"

    else:
        Template = ""

    return Template


def main(request):

    currPlant = switchPlant()
    print(currPlant)
    PlantState = readAlarm(currPlant)
    Template = setTemplate(currPlant)
    HTMLData = retrieveData(currPlant, PlantState)

    return render(request, Template, context=HTMLData)
