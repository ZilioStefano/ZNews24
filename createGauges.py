import numpy as np
import panel as pn
import pandas as pd


def ExpectedEta(lastQ, Plant):

    FileName = "rendimentoReale"+Plant+".csv"
    CurvaRendimento = pd.read_csv(FileName)

    QTeo = CurvaRendimento["QOut"]
    if Plant != "TF" and Plant != "SA3":
        QTeo = QTeo / 1000

    etaTeo = CurvaRendimento["etaOut"]
    etaDev = CurvaRendimento["devEta"]


    # cerco i valori più vicini last Q

    i = 0
    while lastQ > QTeo.iloc[i]:
        i = i +1

    if i != 0:
        etaAspettato = (etaTeo[i-1] + etaTeo[i])/2
        devAspettato = 0.5 * np.sqrt(etaDev[i-1]**22 + etaDev[i]**2)
    else:
        etaAspettato = (etaTeo[i] + etaTeo[i])/2
        devAspettato = 0.5 * np.sqrt(etaDev[i]**22 + etaDev[i]**2)

    etaMin = etaAspettato - devAspettato
    etaMax = etaAspettato + devAspettato

    return etaAspettato, etaMin, etaMax


def createPowerGauge(Data):

    lastP = Data["lastP"]
    lastBar = Data["last pressure"]
    lastQ = Data["lastQ"]

    etaAspettato = Data["DatiRef"]["etaRef"]
    etaDev = Data["DatiRef"]["devEta"]

    rho = 1000
    g = 9.81

    PMinus = (etaAspettato - etaDev) * rho * g * lastQ * lastBar * 10.1974 / 1000
    PPlus = (etaAspettato + etaDev) * rho * g * lastQ * lastBar * 10.1974 / 1000

    if np.isnan(lastP) == 0:
        fig = pn.indicators.Gauge(
            name="P", value=round(lastP), bounds=(0, Data["PMax"]), format='{value} kW',
            colors=[(PMinus / Data["PMax"], 'red'), (PPlus / Data["PMax"], 'gold'), (1, 'green')],
            annulus_width=5,
        )
    else:
        fig = pn.indicators.Gauge(
            name="O", value=lastP, bounds=(0, Data["PMax"]), format='{value} kW',
            colors=[(PMinus / Data["PMax"], 'red'), (PPlus / Data["PMax"], 'gold'), (1, 'green')],
            annulus_width=5,
        )

    fig.save('graph.html', embed=True, embed_json=True)

    GaugUp = open('graph.html', 'r')
    GaugeScript = GaugUp.read()

    if lastP < PMinus:
        ledColor = "led-red"
    elif lastP > PPlus:
        ledColor="led-green"
    else:
        ledColor = "led-yellow"

    GaugeData = {"HTML": GaugeScript, "ledColor": ledColor}

    return GaugeData


def createEtaGauge(Data):

    etaMax = 100

    lastQ = Data["lastQ"]
    Plant = Data["Plant"]
    lastEta = Data["lastEta"]

    if Plant != "CST":
        etaAspettato, etaMinus, etaPlus = ExpectedEta(lastQ, Plant)
    else:
        etaAspettato, etaMinus, etaPlus = 0, 0, 0

    name = "\u03b7"

    fig = pn.indicators.Gauge(
        name=name, value=round(100 * lastEta, 1), bounds=(0, etaMax), format='{value} %',
        colors=[(100*etaMinus/etaMax, 'red'), (100*etaPlus/etaMax, 'gold'), (1, 'green')], annulus_width=5,
    )

    fig.save('graph.html', embed=True, embed_json=True)

    GaugUp = open('graph.html','r')

    GaugeScript = GaugUp.read()

    if lastEta < etaMinus:
        ledColor = "led-red"
    elif lastEta > etaPlus:
        ledColor = "led-green"
    else:
        ledColor = "led-yellow"

    DatiRef = {"etaRef": etaAspettato, "devEta": etaAspettato-etaMinus}

    GaugeData = {"HTML": GaugeScript, "DatiRef": DatiRef, "ledColor": ledColor}

    return GaugeData


def createVar2Gauge(Data):

    name = "Q"
    Var2Max = Data["Var2Max"]
    Qudm = Data["udm"]
    QMinus = Data["MeanQ"] - Data["DevQ"]
    QPlus = Data["MeanQ"] + Data["DevQ"]
    lastQ = Data["lastVar2"]
    Plant = Data["Plant"]

    fig2 = pn.indicators.Gauge(
        name=name, value=round(lastQ, 1), bounds=(0, Var2Max), format='{value} '+Qudm,
        colors=[(QMinus/Var2Max, 'red'), (QPlus/Var2Max, 'gold'), (1, 'green')], annulus_width=5
    )

    fig2.save('graph2.html', embed=True, embed_json=True)

    GaugUp = open('graph2.html', 'r')

    GaugeScript = GaugUp.read()

    if lastQ < QMinus:
        ledColor = "led-red"
    elif lastQ > QPlus:
        ledColor = "led-green"
    else:
        ledColor = "led-yellow"

    GaugeData = {"HTML": GaugeScript, "ledColor": ledColor}

    return GaugeData



