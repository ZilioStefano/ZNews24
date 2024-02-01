import csv
from django.shortcuts import render
from ftplib import FTP
import pandas as pd
from indexFuncs import creaGrafico, CreaGraficoRendimenti, creaGraficoCarichi, plotGaugePower, plotGaugeCharge, plotGaugeRad, plotGaugePR, readAlarms
from num2string_001 import convertNumber
import numpy as np
from statistics import mean
from bs4 import BeautifulSoup
import html
from datetime import datetime, timedelta


# Create your views here.
def main(request):
    global NextPlant, currPlant, FilenameDay, lastVar2, lastP, lastPR, PRBGCol
    StatoAllarmi = readAlarms()

    df = pd.read_csv("Current Plant.csv")
    Plant = int(df["Plant"])
    Plant = 4
    # print(Plant)

    print(Plant)
    # Plant = 9

    if Plant == -2:
        PlantTag = "DI"
        NextPlant = -1
        CurrState = StatoAllarmi["DI"]

    elif Plant == -1:
        PlantTag = "SA3"
        NextPlant = 0
        CurrState = StatoAllarmi["SA3"]

    elif Plant == 0:
        PlantTag = "ST"
        NextPlant = 1
        CurrState = StatoAllarmi["ST"]

    elif Plant == 1:
        PlantTag = "PAR"
        NextPlant = 2
        CurrState = StatoAllarmi["Partitore"]

    elif Plant == 2:
        PlantTag = "PG"
        NextPlant = 3
        CurrState = StatoAllarmi["PG"]

    elif Plant == 3:
        PlantTag = "TF"
        NextPlant = 4
        CurrState = StatoAllarmi["TF"]

    elif Plant == 4:
        PlantTag = "SCN"
        NextPlant = 5
        CurrState1 = StatoAllarmi["SCN1"]
        CurrState2 = StatoAllarmi["SCN2"]

        if CurrState1 == "O" and CurrState2 == "O":
            CurrState = "O"
        elif CurrState1 == "A" or CurrState2 == "A":
            CurrState = "A"
        else:
            CurrState = "W"

    elif Plant == 5:
        PlantTag = "Rubino"
        NextPlant = 6
        CurrState = StatoAllarmi["Rubino"]

    elif Plant == 6:
        PlantTag = "CST"
        NextPlant = 7

    elif Plant == 7:
        PlantTag = "H2O"
        NextPlant = 8

    elif Plant == 8:
        PlantTag = "PV"
        NextPlant = 9

    elif Plant == 9:
        PlantTag = "Global"
        NextPlant = -1

    # NextPlant = 0
    # CurrState = "A"
    ftp = FTP("192.168.10.211", timeout=120)
    ftp.login('ftpdaticentzilio', 'Sd2PqAS.We8zBK')

    print(PlantTag)
    if PlantTag == "SCN":

        ftp.cwd('/dati/SCN')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "PV"

        FilenameDay = "SCNDailyPlot.csv"

    elif PlantTag == "RUB":

        ftp.cwd('/dati/Rubino')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "PV"

        FilenameDay = "RubinoDailyPlot.csv"

    elif PlantTag == "ST":

        ftp.cwd('/dati/San_Teodoro')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "H2O"

        FilenameDay = "STDailyPlot.csv"

    elif PlantTag == "PAR":

        ftp.cwd('/dati/San_Teodoro')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "H2O"

        FilenameDay = "PartitoreDailyPlot.csv"

    elif PlantTag == "PG":

        ftp.cwd('/dati/ponte_giurino')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "H2O"

        FilenameDay = "PGDailyPlot.csv"

    elif PlantTag == "TF":

        ftp.cwd('/dati/Torrino_Foresta')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "H2O"

        FilenameDay = "TFDailyPlot.csv"

    elif PlantTag == "SA3":

        ftp.cwd('/dati/SA3')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "H2O"
        FilenameDay = "SA3DailyPlot.csv"

    elif PlantTag == "DI":

        ftp.cwd('/dati/Zilio_Roof/Dual Immobiliare')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "H2O"
        FilenameDay = "DIDailyPlot.csv"

    else:
        ftp.cwd('/dati/Database_Produzione')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "H2O"
        Filename = "Carichi.csv"

    last24h_TL_Filename = PlantTag+"last24hTL.csv"
    last24h_STAT_Filename = PlantTag+"last24hStat.csv"
    Month_TL_Filename = PlantTag+"MonthTL.csv"
    Month_STAT_Filename = PlantTag+"MonthStat.csv"
    Year_TL_Filename = PlantTag+"YearTL.csv"
    Year_STAT_Filename = PlantTag+"YearStat.csv"

    gFile = open(last24h_TL_Filename, "wb")
    ftp.retrbinary("RETR " + last24h_TL_Filename, gFile.write)
    gFile.close()
    df24hTL = pd.read_csv(last24h_TL_Filename)

    gFile = open(last24h_STAT_Filename, "wb")
    ftp.retrbinary("RETR " + last24h_STAT_Filename, gFile.write)
    gFile.close()
    df24hStat = pd.read_csv(last24h_STAT_Filename)

    gFile = open(Month_STAT_Filename, "wb")
    ftp.retrbinary("RETR " + Month_STAT_Filename, gFile.write)
    gFile.close()
    dfMonthStat = pd.read_csv(Month_STAT_Filename)

    gFile = open(Year_STAT_Filename, "wb")
    ftp.retrbinary("RETR " + Year_STAT_Filename, gFile.write)
    gFile.close()
    dfYearStat = pd.read_csv(Year_STAT_Filename)

    ftp.close()

    if Plant < 6 and Plant > -2:
        A = 3

    else:

        gFile = open(Filename, "wb")
        ftp.retrbinary("RETR " + Filename, gFile.write)
        gFile.close()
        df = pd.read_csv(Filename)

    if PlantTag == "RUB" or PlantTag == "SCN":
        G = df24hTL["I"]

        if len(G) > 0:
            lastG = G[len(G) - 1]
            lastVar2, lastVar2Col = convertNumber(lastG, "ERad", "HTML", PlantTag)

            P = df24hTL["P"]
            t = pd.to_datetime(df24hTL["t"])
            t0 = datetime.now()
            t0 = t0 - timedelta(hours=24)

            try:
                E24 = df24hStat["Energy"][0]
            except Exception as err:
                print(err)
                E24 = float('nan')

            lastP = P[len(P) - 1]
            lastP, lastPCol = convertNumber(lastP, "Power", "HTML", PlantTag)
            PR = df24hTL["Eta"]
            lastPR = round(PR[len(PR) - 1], 1)

            PR24 = PR[PR != float('inf')]
            # PR24 = PR24[np.isnan(PR24) == 0]
            # PR24 = str(round(mean(PR24), 1)) + " %"
            PRBGCol = "green"

            if lastPR < 70:
                PRBGCol = "red"

            else:
                PRBGCol = "green"

        else:
            lastP = "No Link"
            lastVar2 = "No Link"
            lastPR = "No Link"
            PRBGCol = "grey"

    elif PlantTag == "TF" or PlantTag == "ST" or PlantTag == "PAR" or PlantTag == "PG" or PlantTag == "SA3":

        Q = df24hTL["Q"]
        lastQ = Q[len(Q)-1]
        lastVar2, lastVar2Col = convertNumber(lastQ, "Charge", "HTML", PlantTag)

        P = df24hTL["P"]

        t = pd.to_datetime(df24hTL["t"])
        t0 = datetime.now()
        t0 = t0 - timedelta(hours=24)
        if len(P[t>=t0])>0:

            E24 = mean(P[t>=t0])*24
        else:
            E24 = 0

        lastP = P[len(P) - 1]
        lastP, lastPCol = convertNumber(lastP, "Power", "HTML", PlantTag)
        PR = df24hTL["Eta"]
        PR24 = PR[PR != float('inf')]

        lastPR = round(PR[len(PR) - 1], 1)

        PRBGCol = "green"

        if lastPR < 80:
            PRBGCol = "red"

        else:
            PRBGCol = "green"

    elif PlantTag == "PV":

        G = df["IPV"]
        lastG = G
        lastVar2, lastVar2Col = convertNumber(lastG[0], "ERad", "HTML", currPlant)

        P = df["PPV"]
        lastP = P[len(P) - 1]

        if np.isnan(lastP):
            lastP = "Ignota"
        else:
            lastP, lastPCol = convertNumber(lastP, "Power", "HTML", currPlant)

        PR = 100 * df["PRPV"]
        lastPR = round(PR[len(PR) - 1], 1)

        PRBGCol = "green"

        if lastPR < 70:
            PRBGCol = "red"

        else:
            PRBGCol = "green"

    elif PlantTag == "CST":
        Q = df["QCST"]

    elif PlantTag == "DI":
        P = df["P"]
        lastP = P[len(P) - 1]
        lastP, lastPCol = convertNumber(lastP, "Power", "HTML", currPlant)

    BlinkCode = open("BlinkCode.html")
    BlinkCode = BlinkCode.read()
    pageColor = "#e2f5ef"

    if Plant < 6:

        if CurrState == "A":
            pageColor = "IndianRed"
        else:
            pageColor = "#e2f5ef"

        if PlantTag == "ST" or PlantTag == "TF" or PlantTag == "PG" or PlantTag == "PAR" or PlantTag == "SA3":
            datiGauge2, LedColor2 = plotGaugeCharge(df24hTL, PlantTag)

        else:
            datiGauge2, LedColor2 = plotGaugeRad(df24hTL, PlantTag)

        datiGaugePR, DatiRef, PRLedColor = plotGaugePR(df24hTL, PlantTag, 0, 0)
        datiGaugePower, PowerLedColor = plotGaugePower(df24hTL, PlantTag, DatiRef)

        if Plant < 6:

            GraphData = creaGrafico(df24hTL, currType, PlantTag, CurrState)
            GraphEta = CreaGraficoRendimenti(df24hTL, currType, Plant, CurrState)

            try:
                if E24 < 0:
                    sign = "-"
                else:
                    sign = ""
                E24, dummy = convertNumber(E24, "Energy", "HTML", PlantTag)
                E24 = sign+E24

            except Exception as err:
                print(err)
                E24 = "No-Link"

            if len(df24hStat["Resa"])>0:
                Corrispettivo24 = convertNumber(df24hStat["Resa"][0], "Money", "HTML", PlantTag)
                Corrispettivo24 = Corrispettivo24[0]
            else:
                Corrispettivo24 = "Ignoto"

            if Plant == -1:
                # PR24 = ""
                Corrispettivo24 = ""
                df2["PRMese"][0] = ""
                df2["PRAnno"][0] = ""
                df2["ResaMese"][0] = ""
                df2["ResaAnno"][0] = ""

            if PlantTag == "Rubino" or PlantTag == "SCN":
                EMese, dummy = convertNumber(dfMonthStat["Energy"][0], "Energy", "HTML", PlantTag)
                CorrMese, dummy = convertNumber(dfMonthStat["Resa"][0], "Money", "HTML", PlantTag)
                CorrMese = CorrMese + "+RID"
                PRMese = str(round(100*dfMonthStat["etaMean"][0], 1))+" %"
                EAnno = dfYearStat["Energy"][0]
                EAnno, dummy = convertNumber(EAnno, "Energy", "HTML", PlantTag)
                PRAnno = 100 * dfYearStat["etaMean"][0]
                PRAnno = str(round(PRAnno, 1))+" %"
                CorrispettivoAnno, dummy = convertNumber(dfYearStat["Resa"][0], "Money", "HTML", PlantTag)
                CorrispettivoAnno = CorrispettivoAnno + "+RID"

                if len(EMese) == 0:
                    EMese = "Ignoto"
                    CorrMese = "Ignoto"
                    PRMese = "Ignoto"
                    CorrispettivoAnno = df2["ResaAnnoFTV"][0] + " + RID"

                else:
                    Corrispettivo24 = Corrispettivo24 + " + RID"

            else:
                EMese, dummy = convertNumber(dfMonthStat["Energy"][0], "Energy", "HTML", PlantTag)
                CorrMese = dfMonthStat["Resa"][0]
                CorrMese, dummy = convertNumber(CorrMese, "Money", "HTML", PlantTag)
                PRMese = 100 * dfMonthStat["etaMean"][0]
                PRMese = str(round(PRMese, 1))+" %"

                EAnno = dfYearStat["Energy"][0]
                EAnno, dummy = convertNumber(EAnno, "Energy", "HTML", PlantTag)

                CorrispettivoAnno, dummy = convertNumber(dfYearStat["Resa"][0], "Money", "HTML", PlantTag)

            Now = datetime.now().strftime("%Y")

            try:
                PR24Mean = np.nanmean(PR24)*100
                PR24Mean = str(round(PR24Mean, 1))+" %"

            except Exception as err:
                print(err)
                PR24Mean = "Ignoto"

            Graphs = {"Current": GraphData["Grafico"], "eta": GraphEta["GraficoRendimenti"], "lastVar2": lastVar2,
                      "lastP": lastP, "lastPR": lastPR, "PRCol": PRBGCol, "Gauge": datiGaugePower, "Gauge2": datiGauge2, "GaugePR": datiGaugePR, "BlinkCode": BlinkCode,
                      "PowerLedColor": PowerLedColor, "LedColor2": LedColor2,"PRLedColor": PRLedColor, "E24": E24,
                      "EMonth": EMese, "EAnno": EAnno, "pageColor": pageColor, "PR24": PR24Mean,
                      "PRMese": PRMese, "PRAnno": PRAnno, "Corrispettivo24": Corrispettivo24,
                      "CorrispettivoMese": CorrMese, "CorrispettivoAnno": CorrispettivoAnno, "Year": Now}

            Template = "index7.html"
            Now = datetime.now().strftime("%Y")

        elif Plant == 6:
            GraphData = creaGraficoCarichi(df, currType, currPlant)
            GraphEta = CreaGraficoRendimenti(df, currType, Plant, CurrState)
            Graphs = {"Current": GraphData["Grafico"], "lastVar2": lastVar2,
                      "lastP": lastP, "lastPR": lastPR, "PRCol": PRBGCol, "MP": MPString, "MPColor": MPColor,
                      "eta": GraphEta["GraficoRendimenti"], "Gauge": datiGauge["Gauge"], "PowerLedColor": PowerLedColor,
                      "LedColor2": LedColor2, "PRLedColor": PRLedColor,"pageColor": pageColor}

            Template = "index7.html"

        else:
            GraphData = creaGraficoCarichi(df, currType, currPlant)
            GraphEta = CreaGraficoRendimenti(df, currType, Plant, CurrState)
        # GraphData = creaGrafico(df, currType, currPlant)
            Graphs = {"Current": GraphData["Grafico"], "lastVar2": lastVar2,
                      "lastP": lastP, "lastPR": lastPR, "PRCol": PRBGCol, "MP": MPString, "MPColor": MPColor,
                      "eta": GraphEta["GraficoRendimenti"], "Gauge": datiGauge["Gauge"]}

            Template = "index.html"

    elif Plant == 6:

        ftp.cwd('/dati/San_Teodoro')

        Filename = "STlast24Plot.csv"

        gFile = open(Filename, "wb")
        ftp.retrbinary("RETR " + Filename, gFile.write)
        gFile.close()
        dfST = pd.read_csv(Filename)

        Filename = "Partitorelast24Plot.csv"

        gFile = open(Filename, "wb")
        ftp.retrbinary("RETR " + Filename, gFile.write)
        gFile.close()
        dfPartitore = pd.read_csv(Filename)
        GraphData = creaGraficoCarichi(df, currType, currPlant)

        # PR = np.divide((dfST["Q"] * dfST["P"] + dfPartitore["Q"] * dfPartitore["P"]) , (dfST["Q"] + dfPartitore["Q"]))

        # PR = np.array(df["CST"])/np.array(df["QCST"])

        # df["PRlast24"] = PR
        # lastPR = PR[len(PR)-1]

        Q = df["QCST"]
        lastQ = Q[len(Q)-1]
        lastVar2, lastVar2Col = convertNumber(lastQ, "Charge", "HTML", currPlant)

        P = df["CST"]
        lastP = P[len(P) - 1]
        lastP, lastPCol = convertNumber(lastP, "Power", "HTML", currPlant)

        PR = 1000*np.divide(P,  9.81 * df["QCST"] * df["hCST"])

        PRBGCol = "red"
        lastPR = PR[len(PR) - 1]

        df["PRlast24"] = 100*PR
        GraphEta = CreaGraficoRendimenti(df, currType, Plant, "O")
        datiGauge2, LedColor2 = plotGaugeCharge(df, currPlant)
        datiGaugePR, DatiRef, PRLedColor = plotGaugePR(df, currPlant, dfST, dfPartitore)
        datiGaugePower, PowerLedColor = plotGaugePower(df, currPlant, DatiRef)
        Now = datetime.now().strftime("%Y")

        Graphs = {"Current": GraphData["Grafico"], "lastVar2": lastVar2,
                  "lastP": lastP, "lastPR": lastPR, "PRCol": PRBGCol,
                  "eta": GraphEta["GraficoRendimenti"],
                  "Gauge": datiGaugePower, "Gauge2": datiGauge2,
                  "GaugePR": datiGaugePR, "PowerLedColor": PowerLedColor, "LedColor2": LedColor2, "PRLedColor": PRLedColor,
                  "pageColor": pageColor, "Year": Now}

        Template = "index8.html"

    else:

        GraphData = creaGraficoCarichi(df, currType, currPlant)

        Template = "index4.html"
        Now = datetime.now().strftime("%Y")

        Graphs = {"Grafico": GraphData["Grafico"], "BlinkCode": BlinkCode, "Year": Now}

    return render(request, Template, context=Graphs)
