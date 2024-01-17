import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import panel as pn
import math
import csv
from statistics import mean
from ftplib import FTP
pd.options.plotting.backend = "plotly"


def readAlarms():

    ftp = FTP("192.168.10.211", timeout=120)
    ftp.login('ftpdaticentzilio', 'Sd2PqAS.We8zBK')
    ftp.cwd('/dati/Database_Produzione')
    gFile = open("AlarmStates.csv", "wb")
    ftp.retrbinary('RETR AlarmStates.csv', gFile.write)
    gFile.close()
    df = pd.read_csv("AlarmStates.csv", on_bad_lines='skip', header='infer', delimiter=';')

    StatoAllarmi = csv.DictReader(open("AlarmStates.csv"))

    for row in StatoAllarmi:
        StatoAllarmi = row

    STState = StatoAllarmi["ST"]
    PGState = StatoAllarmi["PG"]
    SCN1State = StatoAllarmi["SCN1"]
    SCN2State = StatoAllarmi["SCN2"]
    RubinoState = StatoAllarmi["Rubino"]
    PartitoreState = StatoAllarmi["Partitore"]
    TFState = StatoAllarmi["TF"]
    CavarzanState = StatoAllarmi["Cavarzan"]
    SA3State = StatoAllarmi["SA3"]

    return StatoAllarmi


def plotGaugePR(data, Plant,df24ST, df24Partitore):

    udm = "\u03B7 [%]"

    if Plant == "PV":
        I = data["IPV"]
        P = data["PPV"]

        PMax = 997.44 + 926.64
        udm = "PR [%]"

    elif Plant == "ST":
        df = pd.read_csv("rendimentoRealeST.csv")
        QRef = df["QOut"]
        etaRef = df["etaOut"]
        etaDev = df["devEta"]

        PMax = 259.30
        P = data["P"]
        lastP = P[len(P)-1]

        Q = data["Q"]
        lastQ = Q[len(Q)-1]
        name = "\u03b7"

    elif Plant == "SA3":
        df = pd.read_csv("etaTurbSA3.csv")
        QRef = df["QOut"]
        etaRef = df["etaOut"]
        etaDev = 0.1*df["etaOut"]

        PMax = 259.30
        P = data["P"]
        lastP = P[len(P)-1]

        Q = data["Q"]
        lastQ = Q[len(Q)-1]
        name = "\u03b7"
    elif Plant == "Partitore":
        PMax = 100
        P = data["P"]
        Q = data["Q"]
        lastQ = Q[len(Q)-1]
        df = pd.read_csv("rendimentoRealePartitore.csv")
        name = "\u03b7"

    elif Plant == "PG":
        PMax = 248
        P = data["P"]
        Q = data["Q"]
        lastQ = Q[len(Q)-1]
        df = pd.read_csv("rendimentoRealePG.csv")
        name = "\u03b7"

    elif Plant == "TF":
        PMax = 248
        P = data["P"]
        Q = data["Q"]
        lastQ = Q[len(Q) - 1]
        df = pd.read_csv("rendimentoRealeTF.csv")
        name = "\u03b7"

    elif Plant == "Rubino":
        PMax = 997.44
        P = data["P"]
        Q = data["G"]

        if len(Q)>0:
            lastQ = Q[len(Q) - 1]
        else:
            lastQ = float('nan')
        name = "PR"

    elif Plant == "SCN":
        PMax = 926.64
        P = data["P"]
        Q = data["G"]
        lastQ = Q[len(Q) - 1]
        name = "PR"

    elif Plant == "CST":
        try:
            P = data["CST"]
            Q = data["QCST"]
            data.to_csv("prevCST.csv")
        except Exception as err:
            data = pd.read_csv("prevCST.csv")
            P = data["CST"]
            Q = data["QCST"]

        lastQ = Q[len(Q) - 1]
        name = "\u03b7"

    else:
        P = data["P"]
        name = "\u03b7"

    PRMax = 100

    if Plant != "Rubino" and Plant != "SCN" and Plant != "CST":

        # if Plant == "CST":
        #     QRef = 95
        #     etaRef = 1.99
        #     etaDev = 0.06
        #
        # else:
        QRef = df["QOut"]
        etaRef = df["etaOut"]
        if Plant != "SA3":
            etaDev = df["devEta"]
        else:
            etaDev = 0.1*etaRef

        PMax = 259.30
        P = data["P"]
        lastP = P[len(P)-1]

        Q = data["Q"]
        lastQ = Q[len(Q)-1]

        ok = 0
        j = 0

        while ok == 0:

            if lastQ < QRef[0]:
                etaCurr = etaRef[0]
                devCurr = etaDev[0]
                ok = 1

            elif QRef[j] <= lastQ < QRef[j + 1]:
                etaCurr = mean([etaRef[j], etaRef[j+1]])
                devCurr = mean([etaDev[j], etaDev[j + 1]])
                ok = 1

            elif lastQ >= QRef[len(QRef)-1]:
                etaCurr = etaRef[len(etaRef)-1]
                devCurr = etaDev[len(etaDev)-1]
                ok = 1

            else:
                j = j+1

        h = data["h"]
        lasth = h[len(h)-1]

    elif Plant == "CST":

        #San Teodoro

        dfST = pd.read_csv("rendimentoRealeST.csv")
        Filename = "STlast24Plot.csv"

        QRef = dfST["QOut"]
        etaRef = dfST["etaOut"]
        etaDev = dfST["devEta"]

        PMax = 259.30
        P = df24ST["P"]
        lastP = P[len(P)-1]

        Q = df24ST["Q"]
        QST = Q
        lastQ = Q[len(Q)-1]
        lastQST = lastQ

        QRef = dfST["QOut"]
        etaRef = dfST["etaOut"]
        etaDev = dfST["devEta"]

        ok = 0
        j = 0

        while ok == 0:

            if lastQ < QRef[0]:
                etaCurr = etaRef[0]
                devCurr = etaDev[0]
                ok = 1

            elif QRef[j] <= lastQ < QRef[j + 1]:
                etaCurr = mean([etaRef[j], etaRef[j + 1]])
                devCurr = mean([etaDev[j], etaDev[j + 1]])
                ok = 1

            elif lastQ >= QRef[len(QRef) - 1]:
                etaCurr = etaRef[len(etaRef) - 1]
                devCurr = etaDev[len(etaDev) - 1]
                ok = 1

            else:
                j = j + 1

        hST = df24ST["h"]

        etaCurrST = etaCurr
        devST = devCurr

        # Partitore

        dfPartitore = pd.read_csv("rendimentoRealePartitore.csv")

        QRef = dfPartitore["QOut"]
        etaRef = dfPartitore["etaOut"]
        etaDev = dfPartitore["devEta"]

        PMax = 259.30
        P = df24Partitore["P"]
        lastP = P[len(P) - 1]


        Q = df24Partitore["Q"]
        QPartitore = Q
        lastQ = Q[len(Q) - 1]
        lastQPartitore = lastQ

        ok = 0
        j = 0

        while ok == 0:

            if lastQ < QRef[0]:
                etaCurr = etaRef[0]
                devCurr = etaDev[0]
                ok = 1

            elif QRef[j] <= lastQ < QRef[j + 1]:
                etaCurr = mean([etaRef[j], etaRef[j + 1]])
                devCurr = mean([etaDev[j], etaDev[j + 1]])
                ok = 1

            elif lastQ >= QRef[len(QRef) - 1]:
                etaCurr = etaRef[len(etaRef) - 1]
                devCurr = etaDev[len(etaDev) - 1]
                ok = 1

            else:
                j = j + 1

        hPartitore = df24Partitore["h"]

        etaCurrPartitore = etaCurr
        devPartitore = devCurr

        etaCurr = (lastQST * etaCurrST + lastQPartitore * etaCurrPartitore) / (lastQST + lastQPartitore)
        devCurr = np.sqrt(lastQST**2 * devST**2 + lastQPartitore**2 * devPartitore**2) / (lastQST + lastQPartitore)

    else:

        if Plant == "SCN":
            etaCurr = 0.763
            devCurr = 0.0305
            PRMax = 100
        else:
            etaCurr = 0.848
            devCurr = 0.0823
            PRMax = 100


    etaMedio = etaCurr
    devST = devCurr

    etaPlus = etaMedio + devST
    etaMinus = etaMedio - devST


    if len(P)>0:
        lastP = P[len(P)-1]
        PPrec = P[len(P)-2]
        PR = data["PRlast24"]
        lastPR = PR[len(PR) - 1]
        PRPrec = PR[len(PR) - 2]
    else:
        lastP = float('nan')
        lastPR = float('nan')


    if Plant == "CST":
        PRST = df24ST["PRlast24"]
        lastPRST = PRST[len(PRST) - 1]

        PRPartitore = df24Partitore["PRlast24"]
        lastPRPartitore = PRPartitore[len(PRPartitore) - 1]

        lastPR = (lastPRST * lastQST + lastPRPartitore * lastQPartitore) / (lastQPartitore + lastQST)

    PRMax = max(lastPR, PRMax)

    if math.isnan(PRMax):
        PRMax = 100
    # PRMax = float('Nan')
    if Plant =="SCN" or Plant == "Rubino":
        FloatedQuot = PRMax//10
        IncQuot = FloatedQuot+1

        PRMax = round(IncQuot * 10)

    if math.isnan(lastPR):
        lastPR =0
        ledColor = "none"

    else:

        lastPR = round(lastPR, 1)
        if lastPR < 100*etaMinus:
            ledColor = "led-red"
        elif lastPR > 100*etaPlus:
            ledColor="led-green"
        else:
            ledColor="led-yellow"

    if np.isnan(lastPR) or np.isinf(lastPR):
        lastPR = 0

    fig = pn.indicators.Gauge(
        name=name, value=lastPR, bounds=(0, PRMax), format='{value} %',
        colors=[(100*etaMinus/PRMax, 'red'), (100*etaPlus/PRMax, 'gold'), (1, 'green')], annulus_width=5,
    )


    # fig = go.Figure(go.Indicator(
    #     mode="gauge+number+delta",
    #     value=lastPR,
    #     delta={'reference': PRPrec},
    #     gauge={'axis': {'range': [None, PRMax], 'tickwidth': 1, 'tickcolor': "black"},
    #              'steps': [
    #                  {'range': [0, 100*etaMinus], 'color': 'red'},
    #                  {'range': [100*etaMinus, 100 * etaPlus], 'color': 'green'},
    #                  {'range': [100*etaPlus, max(PRMax, lastPR)], 'color': 'blue'}],
    #                 'bar': {'color': "yellow"}
    # },
    #     # domain={'x': [0, PMax], 'y': [0, 1]},
    #     title={'text': udm}))

    # fig.update_layout(width=500)
    # fig.update_layout(paper_bgcolor="#e2f5ef")

    # GraphData = fig.to_html('graph.html')
    GraphData = fig.save('graph.html', embed=True, embed_json=True)

    GraphData = {"Gauge": GraphData}

    # GaugeScript = fig.save('graph.html')
    GaugUp = open('graph.html','r')

    GaugeScript = GaugUp.read()

    DatiRef = {"etaRef": etaMedio, "devEta": devST}

    return GaugeScript, DatiRef, ledColor


def plotGaugeRad(data, Plant):

    I = data["G"]
    P = data["P"]

    QMax = 1300
    P = data["P"]

    if len(P)>0:
        lastP = P[len(P)-1]
        lastI = I[len(I) - 1]
        IPrec = I[len(I) - 2]
    else:
        lastP = "No Link"
        lastI = "No Link"



    etaMedio = 0.594
    devST = 0.022

    etaPlus = etaMedio + devST
    etaMinus = etaMedio - devST

    QLim = 1000

    P = data["P"]

    # lastP = P[len(P)-1]

    name = "GTI"

    IMax = 1300

    if lastI!='No Link':

        if lastI < 700:
            ledColor = "led-red"
        elif lastI > 800:
            ledColor="led-green"
        else:
            ledColor="led-yellow"
        fig = pn.indicators.Gauge(
            name=name, value=round(lastI), bounds=(0, IMax), format='{value} W/m\u00b2',
            colors=[(700/IMax, 'red'),(800/IMax, 'gold'), (IMax/IMax, 'green')], annulus_width=5
        )

    else:
        ledColor = "grey"
        fig = pn.indicators.Gauge(
            name=name, value=float('nan'), bounds=(0, IMax), format='{value} W/m\u00b2',
            colors=[(700 / IMax, 'red'), (800 / IMax, 'gold'), (IMax / IMax, 'green')], annulus_width=5
        )


    # fig = pn.indicators.Gauge(
    #     name=name, value=round(lastI), bounds=(0, IMax), format='{value} W/m\u00b2',
    #     colors=[(700/IMax, 'red'),(800/IMax, 'gold'), (IMax/IMax, 'green')], annulus_width=5
    # )

    GraphData = fig.save('graph.html', embed=True, embed_json=True)

    # GraphData = {"Gauge": GraphData}
    # GraphData = fig.save('graph.html', embed=True, embed_json=True)

    # GaugeScript = fig.save('graph.html')
    GaugUp = open('graph.html', 'r')

    # GaugeScript = GaugUp.read()

    # fig = go.Figure(go.Indicator(
    #
    #     mode="gauge+number+delta",
    #     value=lastQ,
    #     delta={'reference': QPrec},
    #     gauge={'axis': {'range': [None, QMax], 'tickwidth': 1, 'tickcolor': "black"},
    #              'steps': [
    #                  {'range': [0, QLim], 'color': 'red'},
    #                  {'range': [QLim, max(QMax, lastQ)], 'color': 'green'}],
    #                 'bar': {'color': "yellow"},
    #            'bgcolor': "#e2f5ef",
    # },
    #     # domain={'x': [0, PMax], 'y': [0, 1]},
    #     title={'text': Qudm}))
    # fig.update_layout(width=500)
    # fig.update_layout(paper_bgcolor="#e2f5ef")
    GaugeScript = GaugUp.read()

    # fig = go.Figure(go.Indicator(
    #
    #     mode="gauge+number+delta",
    #     value=lastI,
    #     delta={'reference': IPrec},
    #     gauge={'axis': {'range': [None, QMax], 'tickwidth': 1, 'tickcolor': "black"},
    #              'steps': [
    #                  {'range': [0, QLim], 'color': 'red'},
    #                  {'range': [QLim, max(QLim, 1300)], 'color': 'green'}],
    #                 'bar': {'color': "yellow"}
    # },
    #     # domain={'x': [0, PMax], 'y': [0, 1]},
    #     title={'text': "Irraggiamento [W/m\u00b2]"}))
    # fig.update_layout(width=500)
    # fig.update_layout(paper_bgcolor="#e2f5ef")
    # fig.add_annotation(x=0.5, y=0.4, xref='paper', yref='paper')
    #
    # GraphData=fig.to_html('graph.html')

    # GaugeScript = {"Gauge": GraphData}

    return GaugeScript, ledColor


def plotGaugeCharge(data, Plant):

    global QLim
    if Plant == "ST":

        P = data["P"]
        Q = data["Q"]
        h = data["h"]
        QMax = 80
        QLim = 70
        QMedia = 66.8
        QDev = 14.4

    elif Plant == "PG":

        P = data["P"]
        Q = data["Q"]
        h = data["h"]
        QMax = 80
        QLim = 70
        QMedia = 9.77
        QDev = 9.76

    elif Plant == "Partitore":
        P = data["P"]
        Q = data["Q"]
        h = data["h"]
        QMax = 30
        QLim = 25
        QMedia = 22.4
        QDev = 7.8

    elif Plant == "TF":
        P = data["P"]
        Q = data["Q"]
        h = data["h"]
        QMax = 3
        QLim = 1.54
        QMedia = 1.94
        QDev = 0.09
    elif Plant == "SA3":
        P = data["P"]
        Q = data["Q"]
        h = data["h"]
        QMax = 3.60
        QLim = 3.60
        QMedia = 1.80
        QDev = 0.18

    elif Plant == "CST":
        P = data["CST"]
        Q = data["QCST"]
        QMedia = 66.8+22.4
        QDev = 0.5*np.sqrt(14.4**2+7.8**2)

        QMax = 105
        QLim = 95

    else:
        P = data["P"]
        Q = data["Q"]
        h = data["h"]
        lasth = h[len(h) - 1]

    lastP = P[len(P)-1]

    lastQ = Q[len(Q)-1]
    QPrec = Q[len(Q)-2]

    etaMedio = 0.594
    devST = 0.022

    etaPlus = etaMedio + devST
    etaMinus = etaMedio - devST

    QMinus = QMedia - QDev
    QPlus = QMedia + QDev

    Qudm = " l/s"
    if Plant == "TF":
        Qudm = "m\u00b3/s"

    name = "Q"

    if Plant != "TF":
        FloatedQuot = QMax//10
        IncQuot = FloatedQuot+1
        QMax = round(IncQuot*10)


    if lastQ < QMinus:
        ledColor = "led-red"
    elif lastQ > QPlus:
        ledColor = "led-green"
    else:
        ledColor = "led-yellow"

    fig2 = pn.indicators.Gauge(
        name=name, value=round(lastQ, 1), bounds=(0, QMax), format='{value} '+Qudm,
        colors=[(QMinus/QMax, 'red'), (QPlus/QMax, 'gold'), (1, 'green')], annulus_width=5
    )

    GraphData = fig2.save('graph2.html', embed=True, embed_json=True)

    GaugUp = open('graph2.html', 'r')

    GaugeScript = GaugUp.read()

    return GaugeScript, ledColor


def plotGaugePower(data, Plant, DatiRef):

    if Plant == "PV":

        I = data["IPV"]
        P = data["PPV"]
        PMax = 997.44 + 926.64

    elif Plant == "ST":

        PMax = 259.30
        P = data["P"]
        lastP = P[len(P)-1]

        Q = data["Q"]
        lastQ = Q[len(Q)-1]

        h = data["h"]
        lasth = h[len(h)-1]

        etaMedio = DatiRef["etaRef"]
        devST = DatiRef["devEta"]

        etaPlus = etaMedio + devST
        etaMinus = etaMedio - devST

        PMinus = etaMinus * 9.81 * lastQ / 1000 * lasth
        PPlus = etaPlus * 9.81 * lastQ / 1000 * lasth

    elif Plant == "SA3":

        PMax = 250
        P = data["P"]
        lastP = P[len(P)-1]

        Q = data["Q"]
        lastQ = Q[len(Q)-1]

        h = data["h"]
        lasth = h[len(h)-1]

        etaMedio = DatiRef["etaRef"]
        devST = DatiRef["devEta"]

        etaPlus = etaMedio + devST
        etaMinus = etaMedio - devST

        PMinus = etaMinus * 9.81 * lastQ / 1000 * lasth
        PPlus = etaPlus * 9.81 * lastQ / 1000 * lasth

    elif Plant == "Partitore":

        PMax = 100
        P = data["P"]
        lastP = P[len(P)-1]

        Q = data["Q"]
        lastQ = Q[len(Q)-1]
        h = data["h"]
        lasth = h[len(h)-1]

        etaMedio = DatiRef["etaRef"]
        devST = DatiRef["devEta"]

        etaPlus = etaMedio + devST
        etaMinus = etaMedio - devST

        PMinus = etaMinus * 9.81 * lastQ / 1000 * lasth
        PPlus = etaPlus * 9.81 * lastQ / 1000 * lasth

    elif Plant == "PG":

        PMax = 248
        P = data["P"]
        lastP = P[len(P)-1]

        Q = data["Q"]
        lastQ = Q[len(Q)-1]
        h = data["h"]
        lasth = h[len(h)-1]

        etaMedio = DatiRef["etaRef"]
        devST = DatiRef["devEta"]

        etaPlus = etaMedio + devST
        etaMinus = etaMedio - devST

        PMinus = etaMinus * 9.81 * lastQ / 1000 * lasth
        PPlus = etaPlus * 9.81 * lastQ / 1000 * lasth

    elif Plant == "TF":

        PMax = 420
        P = data["P"]
        lastP = P[len(P)-1]

        Q = data["Q"]
        lastQ = Q[len(Q)-1]
        h = data["h"]
        lasth = h[len(h)-1]

        etaMedio = 1000*DatiRef["etaRef"]
        devST = DatiRef["devEta"]

        etaPlus = etaMedio + devST
        etaMinus = etaMedio - devST

        PMinus = etaMinus * 9.81 * lastQ / 1000 * lasth
        PPlus = etaPlus * 9.81 * lastQ / 1000 * lasth

    elif Plant == "Rubino":
        PMax = 997.44
        P = data["P"]
        Q = data["G"]
        etaMedio = 0.8
        devST = 0.1

        etaPlus = etaMedio + devST
        etaMinus = etaMedio - devST
        if len(Q)>0:
            lastQ = Q[len(Q) - 1]


            PMinus = etaMinus * Q[len(Q) - 1] * PMax
            PPlus = etaPlus * Q[len(Q) - 1] * PMax
        else:
            lastQ = float('nan')
            PMinus = 0
            PPlus = 0

    elif Plant == "SCN":
        PMax = 926.64
        P = data["P"]
        Q = data["G"]
        lastQ = Q[len(Q) - 1]

        etaMedio = 0.8
        devST = 0.1

        etaPlus = etaMedio + devST
        etaMinus = etaMedio - devST

        PMinus = etaMinus * Q[len(Q)-1] * PMax / 1000
        PPlus = etaPlus * Q[len(Q)-1] * PMax / 1000

    elif Plant == "CST":

        PMax = 259.30 + 100
        P = data["CST"]
        Q = data["QCST"]
        lastQ = Q[len(Q) - 1]

        etaMedio = 2.0
        devST = 0.06

        etaPlus = etaMedio + devST
        etaMinus = etaMedio - devST

        PMinus = etaMinus * Q[len(Q)-1]
        PPlus = etaPlus * Q[len(Q)-1]

    else:
        P = data["P"]

    if len(P)>0:
        lastP = P[len(P)-1]
        PPrec = P[len(P)-2]
    else:
        lastP = float('nan')

    if lastP < PMinus:
        ledColor = "led-red"
    elif lastP > PPlus:
        ledColor="led-green"
    else:
        ledColor="led-yellow"

    FloatedQuot = PMax//10
    IncQuot = FloatedQuot+1
    PMax = round(IncQuot*10)

    name = "P"

    if np.isnan(lastP)==0:
        fig = pn.indicators.Gauge(
            name=name, value=round(lastP), bounds=(0, PMax), format='{value} kW',
            colors=[(PMinus/PMax, 'red'), (PPlus/PMax, 'gold'), (1, 'green')],
            annulus_width=5,
        )
    else:
        fig = pn.indicators.Gauge(
            name=name, value=lastP, bounds=(0, PMax), format='{value} kW',
            colors=[(PMinus/PMax, 'red'), (PPlus/PMax, 'gold'), (1, 'green')],
            annulus_width=5,
        )

    GraphData = fig.save('graph.html', embed=True, embed_json=True)

    # GraphData = {"Gauge": GraphData}
    # GraphData = fig.save('graph.html', embed=True, embed_json=True)

    # GaugeScript = fig.save('graph.html')
    GaugUp = open('graph.html', 'r')

    # GaugeScript = GaugUp.read()

    # fig = go.Figure(go.Indicator(
    #
    #     mode="gauge+number+delta",
    #     value=lastQ,
    #     delta={'reference': QPrec},
    #     gauge={'axis': {'range': [None, QMax], 'tickwidth': 1, 'tickcolor': "black"},
    #              'steps': [
    #                  {'range': [0, QLim], 'color': 'red'},
    #                  {'range': [QLim, max(QMax, lastQ)], 'color': 'green'}],
    #                 'bar': {'color': "yellow"},
    #            'bgcolor': "#e2f5ef",
    # },
    #     # domain={'x': [0, PMax], 'y': [0, 1]},
    #     title={'text': Qudm}))
    # fig.update_layout(width=500)
    # fig.update_layout(paper_bgcolor="#e2f5ef")
    GaugeScript = GaugUp.read()

    # fig = go.Figure(go.Indicator(
    #
    #     mode="gauge+number+delta",
    #     value=lastP,
    #     delta={'reference': PPrec},
    #     gauge={'axis': {'range': [None, PMax], 'tickwidth': 1, 'tickcolor': "black"},
    #              'steps': [
    #                  {'range': [0, PMinus], 'color': 'red'},
    #                  {'range': [PMinus, PPlus], 'color': 'green'},
    #                  {'range': [PPlus, max(PMax, PPlus)], 'color': 'blue'}],
    #                 'bar': {'color': "yellow"},
    # },
    #     # domain={'x': [0, PMax], 'y': [0, 1]},
    #     title={'text': "Potenza [kW]"}))
    # fig.update_layout(width=500)
    # fig.update_layout(paper_bgcolor="#e2f5ef")
    # GraphData = fig.to_html('graph.html')

    # GaugeScript = {"Gauge": GraphData}

    return GaugeScript, ledColor


def calcolaRendimenti(data, Type, Plant):

    if Type == "PV":
        if Plant == "SCN":
            Pn = 926.64

        elif Plant == "Rubino":
            Pn = 997.44

        G = data["G"]
        P = data["P"]
        t = data["tI"]

        eta = np.divide(P, G) / Pn * 1000 * 100

    else:

        Q = data["Q"]
        P = data["P"]
        t = data["t"]
        h = data["h"]

        eta = np.divide(1000*P, 9.81*np.multiply(Q, h))

        if Plant == "TF":
            eta = eta/1000

    NSamples = len(eta)

    return t, eta


def CreaGraficoRendimenti(Data,type, Plant, CurrState):

    bgColor = 'red'
    # if Plant != 6:
    PR = Data["PRlast24"]
    maxPR = 100
    if CurrState == "W":
        lineColor = 'grey'
    else:
        lineColor = 'orange'



    if type == "PV":
        fig1 = px.line(Data, x="tI", y="PRlast24", template="ggplot2", line_shape='spline')
        fig1.update_traces(line_color=lineColor)

    else:
        t = Data["t"]
        PR = Data["PRlast24"]

        tVal = t[PR < 100]
        PRVal = PR[PR < 100]
        fig1 = px.line(x=tVal, y=PRVal, template="ggplot2", line_shape='spline')
        fig1.update_traces(line_color=lineColor)

    if Plant == 6:
        fig1.update_layout(height=300, width=1700, title_text="Rendimenti", margin=dict(r=230))

    else:
        fig1.update_layout(height=300, width=1700, title_text="Rendimenti", margin=dict(r=165))

    # if CurrState == "A":
    #     fig1.update_layout(paper_bgcolor=bgColor)

    fig1.layout.yaxis.title = "Rendimento [%]"
    fig1.layout.xaxis.title = ""
    # fig1.update_yaxes(range=[min(70,min(PR)), max(maxPR, max(PR))])

    GraphData = fig1.to_html('graph.html')

    Data = {"GraficoRendimenti": GraphData}

    return Data


def creaGrafico(Data, Type, Plant, CurrState):
    template = "ggplot2"

    if CurrState == "W":
        AreaColor = "grey"
        lineColor = "grey"

    else:

        if Type == "PV":
            lineColor = 'orange'
            AreaColor = 'green'
        else:
            lineColor = 'blue'
            AreaColor = 'green'

    if CurrState == "A":
        bgColor = 'red'
    else:
        bgColor = 'grey'

    if Plant == "PV":
        P = Data["PPV"]
    else:
        P = Data["P"]
    if len(P)>0:
        PMax = max(P)
        PMin = min(P)
        lastP = P[len(P)-1]

    else:
        PMax = 0
        PMin = 0
        lastP = float('nan')

    if Type == "PV":
        y2 = Data["G"]

        if len(y2)>0:
            y2Max = max(y2)
            y2Min = min(y2)
        else:
            y2Max = 0
            y2Min = 0

        time = Data["tI"]
        fig = px.area(Data, x="tP", y="P", template=template)

    else:
        y2 = Data["Q"]
        y2Max = max(y2)
        y2Min = min(y2)
        time = Data["t"]
        fig = px.area(Data, x="t", y="P", template=template)

    # if len(lastT)>0:
    #     lastT = time[len(time)-1]
    # else:
    #     lastT
    fig.update_yaxes(range=[min(0, PMin), max(200, PMax)])
    fig.update_traces(line_color=AreaColor)
    subfig = make_subplots(specs=[[{"secondary_y": True}]])

    if Type == "PV":

        fig2 = px.line(Data, x="tI", y="G", template=template)
    else:
        fig2 = px.line(Data, x="t", y="Q", template=template)

    # fig2.update_yaxes(range=[min(0, QMin), max(80, QMax)])
    fig2.update_traces(yaxis="y2")

    if Type == "PV":
        fig2.update_traces(line_color=lineColor)
    else:
        fig2.update_traces(line_color=lineColor)

    # subfig = fig.data + fig2.data
    subfig.add_traces(fig.data + fig2.data)
    # subfig.add_traces(fig.data + fig2.data)
    subfig.layout.xaxis.title = ""
    subfig.layout.yaxis.title = "Potenza [kW]"
    subfig.layout.yaxis.color = "green"

    if Type == "PV":
        subfig.layout.yaxis2.title = "Irraggiamento [W/m^2]"
        subfig.layout.yaxis2.color = "orange"

    else:
        subfig.layout.yaxis2.color = "blue"

        if Plant != "TF":
            subfig.layout.yaxis2.title = "Portata [l/s]"

        else:
            subfig.layout.yaxis2.title = "Portata [m^3/s]"

    TitleChSize = 30
    if Plant == "SCN":

        subfig.update_layout(height=1300, width=1700, title_text="SCN Pilota",title_font=dict(size=TitleChSize))
        PMaxScala = 926.64
        SecondMaxScala = 1300

    elif Plant == "Rubino":
        subfig.update_layout(height=400, width=1700, title_text="Rubino",title_font=dict(size=TitleChSize))
        PMaxScala = 997.44
        SecondMaxScala = 1300

    elif Plant == "ST":
        subfig.update_layout(height=400, width=1700, title_text="San Teodoro",title_font=dict(size=TitleChSize))
        PMaxScala = 259.30
        SecondMaxScala = 80

    elif Plant == "Partitore":
        subfig.update_layout(height=400, width=1700, title_text="Partitore",title_font=dict(size=TitleChSize))
        PMaxScala = 100
        SecondMaxScala = 25

    elif Plant == "PG":
        subfig.update_layout(height=400, width=1700, title_text="Ponte Giurino",title_font=dict(size=TitleChSize))
        PMaxScala = 248
        SecondMaxScala = 80
    elif Plant == "SA3":
        subfig.update_layout(height=400, width=1700, title_text="SA3",title_font=dict(size=TitleChSize))
        PMaxScala = 250
        SecondMaxScala = 3

    elif Plant == "TF":
        subfig.update_layout(height=400, width=1700, title_text="Torrino Foresta",title_font=dict(size=TitleChSize))
        PMaxScala = 420
        SecondMaxScala = 1.54

    subfig.layout.yaxis2.color = "blue"

    subfig.update_layout(template=template, height=400, width=1700)
    # if CurrState == "A":
    #     subfig.update_layout(paper_bgcolor=bgColor)

    subfig.update_layout({'yaxis': {'range': [min(0, PMin), max(PMaxScala, PMax)]}})
    subfig.update_layout({'yaxis2': {'range': [min(0, y2Min), max(SecondMaxScala, y2Max)]}})

    GraphData = subfig.to_html('graph.html')

    Data = {"Grafico": GraphData}

    # return render(request, 'index.html', {'graphic': graphic})
    return Data


def creaGraficoCarichi(df, currType, currPlant):

    TitleChSize = 30

    if currPlant == "CST":

        PMaxScala = 259.30 + 100
        t = df["t"]
        EPartitore = df["Partitore"]
        EST = df["ST"]
        ECST = df["CST"]
        QCST = df["QCST"]
        QCST = np.array(QCST)

        SecondMaxScala = 95

        dfPlot = {"t": t, "CST": ECST, "ST": EST, "Partitore": EPartitore,"QCST": QCST}

        dfPlot = pd.DataFrame.from_dict(dfPlot)
        PMax = max(ECST)
        PMin = min(ECST)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig1 = dfPlot.plot.area(x="t", y=["ST", "Partitore"], labels={"ST": "San Teodoro", "Partitore": "Partitore"})
        fig2 = dfPlot.plot.line(x="t", y="QCST")
        fig2.update_traces(yaxis="y2")
        QMax = max(QCST)
        Qmin = min(QCST)
        fig.update_layout({'yaxis2': {'range': [min(0, Qmin), max(SecondMaxScala, QMax)]}})
        fig.layout.yaxis2.title = "Portata media condotta [l/s]"

        fig.add_traces(fig1.data + fig2.data)
        fig.update_layout(template="ggplot2", height=400, width=1700, title_text="Condotta San Teodoro",title_font=dict(size=TitleChSize))

    elif currPlant == "H2O":

        PMaxScala = 259.30 + 100 + 248 + 420
        t = df["t"]
        EPartitore = df["Partitore"]
        EST = df["ST"]
        ECST = df["CST"]
        EPG = df["PG"]
        ETF = df["TF"]
        ESA3 = df["SA3"]

        ETot = df["H2O"]

        dfPlot = {"t": t, "Torrino Foresta": ETF, "San Teodoro": EST, "Ponte Giurino": EPG, "Partitore": EPartitore, "SA3": ESA3}
        dfPlot = pd.DataFrame.from_dict(dfPlot)
        PMax = max(ETot)
        PMin = min(ETot)

        fig = dfPlot.plot.area(x="t", y=["Torrino Foresta", "San Teodoro", "Ponte Giurino", "Partitore", "SA3"])
        fig.update_layout(template="ggplot2", height=500, width=1700, title_text="Idroelettrico Zilio",title_font=dict(size=TitleChSize))
        fig.update_layout(template="ggplot2", height=800, width=1700)

    elif currPlant == "PV":
        PMaxScala = 926 + 997
        t = df["t"]
        ESCN = df["SCN"]
        ERubino = df["Rubino"]
        EPV = df["EPV"]

        dfPlot = {"t": t, "SCN Pilota": ESCN, "Rubino": ERubino}
        dfPlot = pd.DataFrame.from_dict(dfPlot)
        PMax = max(EPV)
        PMin = min(EPV)

        fig = dfPlot.plot.area(x="t", y=["SCN Pilota", "Rubino"])
        fig.update_layout(template="ggplot2", height=500, width=1700, title_text="Fotovoltaico Zilio", title_font=dict(size=TitleChSize))
        fig.update_layout(template="ggplot2", height=800, width=1700)

    elif currPlant == "Global":
        PMaxScala = 926 + 997 + 259.30 + 100 + 248 + 420 + 250
        t = df["t"]
        EH2O = df["H2O"]
        EPV = df["EPV"]
        ETot = df["Tot"]

        dfPlot = {"t": t, "H2O": EH2O, "PV": EPV}
        dfPlot = pd.DataFrame.from_dict(dfPlot)
        PMax = max(ETot)
        PMin = min(ETot)

        fig = dfPlot.plot.area(x="t", y=["H2O", "PV"])
        fig.update_layout(title_text="Parco impianti Zilio",title_font=dict(size=TitleChSize))
        fig.update_layout(template="ggplot2", height=800, width=1700)

    fig.update_layout({'yaxis': {'range': [min(0, PMin), max(PMaxScala, PMax)]}})
    fig.layout.yaxis.title = "Energia Prodotta [kWh]"
    GraphData = fig.to_html('graph.html')

    Data = {"Grafico": GraphData}

    return Data
