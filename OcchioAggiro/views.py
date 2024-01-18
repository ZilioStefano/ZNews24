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

    # 1. leggo l'impianto corrente dal server
    # 2. Aggiorno l'impianto corrente nel server
    # 3. scarico i dati relativi all'impianto
    # 3. Faccio il grafico
    # 4. Ripeto dopo 60 secondi

    df = pd.read_csv("Current Plant.csv")
    Plant = int(df["Plant"])
    # Plant = -1
    # print(Plant)

    print(Plant)
    # Plant = 9

    if Plant == -2:
        currPlant = "DI"
        NextPlant = -1
        CurrState = StatoAllarmi["DI"]

    elif Plant == -1:
        currPlant = "SA3"
        NextPlant = 0
        CurrState = StatoAllarmi["SA3"]

    elif Plant == 0:
        currPlant = "ST"
        NextPlant = 1
        CurrState = StatoAllarmi["ST"]

    elif Plant == 1:
        currPlant = "Partitore"
        NextPlant = 2
        CurrState = StatoAllarmi["Partitore"]

    elif Plant == 2:
        currPlant = "PG"
        NextPlant = 3
        CurrState = StatoAllarmi["PG"]

    elif Plant == 3:
        currPlant = "TF"
        NextPlant = 4
        CurrState = StatoAllarmi["TF"]

    elif Plant == 4:
        currPlant = "SCN"
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
        currPlant = "Rubino"
        NextPlant = 6
        CurrState = StatoAllarmi["Rubino"]

    elif Plant == 6:
        currPlant = "CST"
        NextPlant = 7

    elif Plant == 7:
        currPlant = "H2O"
        NextPlant = 8

    elif Plant == 8:
        currPlant = "PV"
        NextPlant = 9

    elif Plant == 9:
        currPlant = "Global"
        NextPlant = -1

    # NextPlant = 0
    # CurrState = "A"
    ftp = FTP("192.168.10.211", timeout=120)
    ftp.login('ftpdaticentzilio', 'Sd2PqAS.We8zBK')

    print(currPlant)
    if currPlant == "SCN":
        Filename = "SCNlast24Plot.csv"
        Filename2 = "SCNDataHTML.csv"

        ftp.cwd('/dati/SCN')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "PV"

        FilenameDay = "SCNDailyPlot.csv"

    elif currPlant == "Rubino":
        Filename = "Rubinolast24Plot.csv"
        Filename2 = "RubinoDataHTML.csv"

        ftp.cwd('/dati/Rubino')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "PV"

        FilenameDay = "RubinoDailyPlot.csv"

    elif currPlant == "ST":
        Filename = "STlast24Plot.csv"
        Filename2 = "STDataHTML.csv"

        ftp.cwd('/dati/San_Teodoro')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "H2O"

        FilenameDay = "STDailyPlot.csv"

    elif currPlant == "Partitore":
        Filename = "Partitorelast24Plot.csv"
        Filename2 = "PartitoreDataHTML.csv"

        ftp.cwd('/dati/San_Teodoro')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "H2O"

        FilenameDay = "PartitoreDailyPlot.csv"

    elif currPlant == "PG":
        Filename = "PGlast24Plot.csv"
        Filename2 = "PGDataHTML.csv"

        ftp.cwd('/dati/ponte_giurino')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "H2O"

        FilenameDay = "PGDailyPlot.csv"

    elif currPlant == "TF":
        Filename = "TFlast24Plot.csv"
        Filename2 = "TFDataHTML.csv"

        ftp.cwd('/dati/Torrino_Foresta')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "H2O"

        FilenameDay = "TFDailyPlot.csv"

    elif currPlant == "SA3":
        Filename = "SA3last24Plot.csv"
        Filename2 = "SA3DataHTML.csv"

        ftp.cwd('/dati/SA3')
        lastPlant = {"Plant": NextPlant}
        df = pd.DataFrame.from_dict([lastPlant])
        df.to_csv("Current Plant.csv")
        currType = "H2O"
        FilenameDay = "SA3DailyPlot.csv"

    elif currPlant == "DI":
        Filename = "DIlast24Plot.csv"
        Filename2 = "DIDataHTML.csv"

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

    if Plant < 6 and Plant > -2:
        gFile = open(Filename, "wb")
        ftp.retrbinary("RETR " + Filename, gFile.write)
        gFile.close()
        df = pd.read_csv(Filename)

        # gFileDay = open(FilenameDay, "wb")
        # ftp.retrbinary("RETR " + FilenameDay, gFileDay.write)
        # gFileDay.close()

        gFile2 = open(Filename2, "wb")
        ftp.retrbinary("RETR " + Filename2, gFile2.write)
        gFile2.close()

        df2 = pd.read_csv(open(Filename2))


    else:

        gFile = open(Filename, "wb")
        ftp.retrbinary("RETR " + Filename, gFile.write)
        gFile.close()
        df = pd.read_csv(Filename)

    if currPlant == "Rubino" or currPlant == "SCN":
        G = df["G"]
        if len(G) > 0:
            lastG = G[len(G) - 1]
            lastVar2, lastVar2Col = convertNumber(lastG, "ERad", "HTML", currPlant)

            P = df["P"]
            t = pd.to_datetime(df["tP"])
            t0 = datetime.now()
            t0 = t0 - timedelta(hours=24)
            try:
                E24 = mean(P[t >= t0]) * 24
            except Exception as err:
                print(err)
                E24 = float('nan')

            lastP = P[len(P) - 1]
            lastP, lastPCol = convertNumber(lastP, "Power", "HTML", currPlant)
            PR = df["PRlast24"]
            lastPR = round(PR[len(PR) - 1], 1)

            PR24 = PR[PR != float('inf')]
            PR24 = PR24[np.isnan(PR24) == 0]
            PR24 = str(round(mean(PR24), 1)) + " %"
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
            PR24 = ""

    elif currPlant == "TF" or currPlant == "ST" or currPlant == "Partitore" or currPlant == "PG" or currPlant == "SA3":

        Q = df["Q"]
        lastQ = Q[len(Q)-1]
        lastVar2, lastVar2Col = convertNumber(lastQ, "Charge", "HTML", currPlant)

        P = df["P"]

        t = pd.to_datetime(df["t"])
        t0 = datetime.now()
        t0 = t0 - timedelta(hours=24)
        if len(P[t>=t0])>0:
            E24 = mean(P[t>=t0])*24
        else:
            E24 = 0

        lastP = P[len(P) - 1]
        lastP, lastPCol = convertNumber(lastP, "Power", "HTML", currPlant)
        PR = df["PRlast24"]
        PR24 = PR[PR != float('inf')]
        PR24 = PR24[np.isnan(PR24) == 0]

        if np.isnan(PR24).all():
            PR24 = ""
        else:
            PR24 = str(round(mean(PR24[PR24<100]), 1)) +" %"

        lastPR = round(PR[len(PR) - 1], 1)

        PRBGCol = "green"

        if lastPR < 80:
            PRBGCol = "red"

        else:
            PRBGCol = "green"

    elif currPlant == "PV":

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

    elif currPlant == "CST":
        Q = df["QCST"]

    elif currPlant == "DI":
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

        if Plant < 6:
            MP = np.array(df["MancataProduzione"])
        else:
            MP = np.array(df["MPPV"])

        if currPlant == "ST" or currPlant == "TF" or currPlant == "PG" or currPlant == "Partitore" or currPlant=="SA3":
            datiGauge2, LedColor2 = plotGaugeCharge(df, currPlant)

        else:
            datiGauge2, LedColor2 = plotGaugeRad(df, currPlant)

        datiGaugePR, DatiRef, PRLedColor = plotGaugePR(df, currPlant,0,0)
        datiGaugePower, PowerLedColor = plotGaugePower(df, currPlant, DatiRef)


        # if MP[0] > 0:
        #     MPColor = "red"
        #     MPString, col = convertNumber(MP[0], "Money", "PDF", currPlant)
        #
        # else:
        #     MPColor = "green"
        #     MPString = "0,00"

        if Plant < 6:
            GraphData = creaGrafico(df, currType, currPlant, CurrState)
            GraphEta = CreaGraficoRendimenti(df, currType, Plant, CurrState)

            try:
                if E24<0:
                    sign="-"
                else:
                    sign=""
                E24, dummy = convertNumber(E24, "Energy", "HTML", currPlant)
                E24 = sign+E24
            except Exception as err:
                print(err)
                E24 = "No-Link"

            if len(df["Corrispettivo"])>0:
                Corrispettivo24 = convertNumber(df["Corrispettivo"][0], "Money", "HTML", currPlant)
                Corrispettivo24 = Corrispettivo24[0]
            else:
                Corrispettivo24 = "Ignoto"

            if Plant == -1:
                PR24 = ""
                Corrispettivo24 = ""
                df2["PRMese"][0] = ""
                df2["PRAnno"][0] = ""
                df2["ResaMese"][0] = ""
                df2["ResaAnno"][0] = ""

            if currPlant == "Rubino" or currPlant == "SCN":
                EMese = df["EIncMese"]
                CorrMese = df["CorrMese"]
                PRMese = df2["PRMese"]

                if len(EMese) == 0:
                    EMese = "Ignoto"
                    CorrMese = "Ignoto"
                    PRMese = "Ignoto"
                    CorrispettivoAnno = df2["ResaAnnoFTV"][0] + " + RID"

                else:
                    EMese = df["EIncMese"][0]
                    CorrMese = str(df["CorrMese"][0])+ " + RID"
                    PRMese = df2["PRMese"][0]
                    Corrispettivo24 = Corrispettivo24 + " + RID"
                    CorrispettivoAnno = df2["ResaAnnoFTV"][0] + " + RID"

            else:
                EMese = df2["EMese"][0]
                CorrMese = df2["ResaMese"][0]
                PRMese = df2["PRMese"][0]
                CorrispettivoAnno = df2["ResaAnno"][0]
            Now = datetime.now().strftime("%Y")

            Graphs = {"Current": GraphData["Grafico"], "eta": GraphEta["GraficoRendimenti"], "lastVar2": lastVar2,
                      "lastP": lastP, "lastPR": lastPR, "PRCol": PRBGCol, "Gauge": datiGaugePower, "Gauge2": datiGauge2, "GaugePR": datiGaugePR, "BlinkCode": BlinkCode,
                      "PowerLedColor": PowerLedColor, "LedColor2": LedColor2,"PRLedColor": PRLedColor, "E24": E24,
                      "EMonth": EMese, "EAnno": df2["EAnno"][0], "pageColor": pageColor, "PR24": PR24,
                      "PRMese": PRMese, "PRAnno": df2["PRAnno"][0], "Corrispettivo24": Corrispettivo24,
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
