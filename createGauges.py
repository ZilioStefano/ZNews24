import numpy as np
import panel as pn
import pandas as pd
pn.extension('echarts')


def ExpectedEta(lastVar2, Plant, lastVar3):

    if Plant =="SA3":

        FileName = "rendimentoReale"+Plant+".csv"
        CurvaRendimento = pd.read_csv(FileName)

        QTeo = CurvaRendimento["QOut"]
        if Plant != "TF" and Plant != "SA3":
            QTeo = QTeo / 1000

        etaTeo = CurvaRendimento["etaOut"]
        etaDev = CurvaRendimento["devEta"]

        # cerco i valori più vicini last Q

        i = 0
        while lastVar2 > QTeo.iloc[i]:
            i = i + 1

        if i != 0:
            etaAspettato = (etaTeo[i-1] + etaTeo[i])/2
            devAspettato = 0.5 * np.sqrt(etaDev[i-1]**22 + etaDev[i]**2)
        else:
            etaAspettato = (etaTeo[i] + etaTeo[i])/2
            devAspettato = 0.5 * np.sqrt(etaDev[i]**2 + etaDev[i]**2)

        etaMin = etaAspettato - devAspettato
        etaMax = etaAspettato + devAspettato

    else:
        
        if Plant != "TF" and Plant != "SA3" and Plant != "SCN":
            lastVar2 = lastVar2 * 1000
        
        MeanFile = "MeanEta"+Plant+".csv"
        DevFile = "DevEta"+Plant+".csv"

        CurvaRendimento = pd.read_csv(MeanFile, header=None)
        devRendimento = pd.read_csv(DevFile, header=None)

        AsseVar2 = CurvaRendimento.iloc[0, 1:]
        AsseVar3 = CurvaRendimento.iloc[1:, 0]

        # cerco i valori più vicini last Q
        
        i = 0
        Var2Test = AsseVar2.iloc[i]
        print(len(AsseVar2))

        while lastVar2 > Var2Test and i < len(AsseVar2)-1:
            print(str(i))
            i = i + 1
            Var2Test = AsseVar2.iloc[i]

        j = 0
        Var3Test = AsseVar3.iloc[j]
        
        if np.isnan(lastVar3):
            lastVar3 = 0
        FinalJ = 1
        while lastVar3 > Var3Test and j < len(AsseVar3):
            j = j + 1
            if j >= len(AsseVar3):
                FinalJ = j-1
                Var3Test = AsseVar3.iloc[FinalJ]

            else:
                FinalJ = j
                Var3Test = AsseVar3.iloc[FinalJ]

        etaAspettato = CurvaRendimento.iloc[FinalJ, i]
        if np.isnan(etaAspettato):
            etaAspettato = np.mean([CurvaRendimento.iloc[FinalJ-1, i], CurvaRendimento.iloc[FinalJ+1, i],
                                 CurvaRendimento.iloc[FinalJ, i-1], CurvaRendimento.iloc[FinalJ, i+1]])

        devAspettato = devRendimento.iloc[FinalJ, i]

        etaMin = etaAspettato - devAspettato
        etaMax = etaAspettato + devAspettato

    return etaAspettato, etaMin, etaMax


def createPowerGauge(Data):

    PN = Data["PN"]

    lastP = Data["lastP"]
    lastVar3 = Data["lastVar3"]
    lastVar2 = Data["lastVar2"]

    etaAspettato = Data["DatiRef"]["etaRef"]
    etaDev = Data["DatiRef"]["devEta"]

    rho = 1000
    g = 9.81

    if Data["Plant"] == "SCN" or Data["Plant"] == "RUB":
        PMinus = (etaAspettato - etaDev) * lastVar2 * PN / 1000
        PPlus = (etaAspettato + etaDev) * lastVar2 * PN / 1000

    else:
        PMinus = (etaAspettato - etaDev) * rho * g * lastVar2 * lastVar3 * 10.1974 / 1000
        PPlus = (etaAspettato + etaDev) * rho * g * lastVar2 * lastVar3 * 10.1974 / 1000

    if lastP < PMinus:
        ledColor = "led-red"
        value_color = "red"

    elif lastP > PPlus:
        ledColor = "led-green"
        value_color = "green"

    else:
        ledColor = "led-yellow"
        value_color = "black"

    pointer_path = 'path://M2090.36389,615.30999 L2090.36389,615.30999 C2091.48372,615.30999 2092.40383,616.194028 2092.44859,617.312956 L2096.90698,728.755929 C2097.05155,732.369577 2094.2393,735.416212 2090.62566,735.56078 C2090.53845,735.564269 2090.45117,735.566014 2090.36389,735.566014 L2090.36389,735.566014 C2086.74736,735.566014 2083.81557,732.63423 2083.81557,729.017692 C2083.81557,728.930412 2083.81732,728.84314 2083.82081,728.755929 L2088.2792,617.312956 C2088.32396,616.194028 2089.24407,615.30999 2090.36389,615.30999 Z'

    if np.isnan(lastP) == 0:
        shownP = round(lastP)
    else:
        shownP = 0

    fig = pn.indicators.Gauge(
        name="P", value=shownP, bounds=(0, Data["PMax"]), format='{value} kW',
        colors=[(PMinus / Data["PMax"], 'red'), (PPlus / Data["PMax"], 'gold'), (1, 'green')],
        annulus_width=5,
        custom_opts={"pointer": {"itemStyle": {"color": "black"}, 'icon': pointer_path}, "value": {"color": "black"},
                     "axisLabel": {
                         "color": 'black', "fontSize": 10,
                     }, "detail": {"color": value_color,
                                   "fontSize": 14}, "series": {"color": 'black', "fontSize": 2},
                     "radius": '90%', "nan_format": "-"}
    )

    fig.width = 250
    fig.height = 250
    fig.save('graph.html', embed=True, embed_json=True)

    GaugUp = open('graph.html', 'r')
    GaugeScript = GaugUp.read()

    GaugeData = {"HTML": GaugeScript, "ledColor": ledColor}

    return GaugeData


def createEtaGauge(Data):

    etaMax = 100

    lastVar2 = Data["lastVar2"]
    lastVar3 = Data["lastVar3"]
    Plant = Data["Plant"]
    lastEta = Data["lastEta"]

    if Plant == "CST":
        etaAspettatoST, etaMinusST, etaPlusST = ExpectedEta(lastVar2, "ST", lastVar3)
        etaAspettatoPAR, etaMinusPAR, etaPlusPAR = ExpectedEta(lastVar2, "PAR", lastVar3)

        etaAspettato = (70*etaAspettatoST + 25*etaAspettatoPAR)/95
        devEtaST = etaAspettatoST - etaMinusST
        devEtaPAR = etaAspettatoPAR - etaMinusPAR
        DevEta = np.sqrt((70*devEtaST)**2 + (25*devEtaPAR)**2)/95
        etaMinus = etaAspettato - DevEta
        etaPlus = etaAspettato + DevEta

    elif Plant != "SA3":
        etaAspettato, etaMinus, etaPlus = ExpectedEta(lastVar2, Plant, lastVar3)
    else:
        etaAspettato, etaMinus, etaPlus = 0, 0, 0

    name = Data["etaName"]
    if lastEta < etaMinus:
        ledColor = "led-red"
        value_color = "red"
    elif lastEta > etaPlus:
        ledColor = "led-green"
        value_color = "green"
    else:
        ledColor = "led-yellow"
        value_color = "black"

    pointer_path = 'path://M2090.36389,615.30999 L2090.36389,615.30999 C2091.48372,615.30999 2092.40383,616.194028 2092.44859,617.312956 L2096.90698,728.755929 C2097.05155,732.369577 2094.2393,735.416212 2090.62566,735.56078 C2090.53845,735.564269 2090.45117,735.566014 2090.36389,735.566014 L2090.36389,735.566014 C2086.74736,735.566014 2083.81557,732.63423 2083.81557,729.017692 C2083.81557,728.930412 2083.81732,728.84314 2083.82081,728.755929 L2088.2792,617.312956 C2088.32396,616.194028 2089.24407,615.30999 2090.36389,615.30999 Z'

    if np.isnan(lastEta) == 0:
        shownEta = round(100 * lastEta, 1)
    else:
        shownEta = 0

    fig = pn.indicators.Gauge(
        name=name, value=shownEta, bounds=(0, etaMax), format='{value} %',
        colors=[(100*etaMinus/etaMax, 'red'), (100*etaPlus/etaMax, 'gold'), (1, 'green')], annulus_width=5,
        custom_opts={"pointer": {"itemStyle": {"color": "black"}, 'icon': pointer_path}, "value": {"color": "black"},
                                          "axisLabel": {
                                              "color": 'black', "fontSize": 10,
                                          },

                                          "detail": {"color": value_color,
                                                        "fontSize": 14},
                     "radius": '90%', "nan_format": "-"}
    )
    # gauge_pane = pn.pane.ECharts(fig, width=100, height=100)

    fig.width = 250
    fig.height = 250
    fig.save('graph.html')#, embed=True, embed_json=True)

    GaugUp = open('graph.html', 'r')

    GaugeScript = GaugUp.read()

    DatiRef = {"etaRef": etaAspettato, "devEta": etaAspettato-etaMinus}

    GaugeData = {"HTML": GaugeScript, "DatiRef": DatiRef, "ledColor": ledColor}

    return GaugeData


def createVar2Gauge(Data):

    name = Data["Var2name"]
    Var2Max = Data["Var2Max"]
    Var2udm = Data["udm"]
    Var2Minus = Data["MeanVar2"] - Data["DevVar2"]
    Var2Plus = Data["MeanVar2"] + Data["DevVar2"]
    lastVar2 = Data["lastVar2"]
    Plant = Data["Plant"]

    if lastVar2 < Var2Minus:
        ledColor = "led-red"
        value_color ="red"

    elif lastVar2 > Var2Plus:
        ledColor = "led-green"
        value_color ="green"

    else:
        ledColor = "led-yellow"
        value_color ="black"

    pointer_path = 'path://M2090.36389,615.30999 L2090.36389,615.30999 C2091.48372,615.30999 2092.40383,616.194028 2092.44859,617.312956 L2096.90698,728.755929 C2097.05155,732.369577 2094.2393,735.416212 2090.62566,735.56078 C2090.53845,735.564269 2090.45117,735.566014 2090.36389,735.566014 L2090.36389,735.566014 C2086.74736,735.566014 2083.81557,732.63423 2083.81557,729.017692 C2083.81557,728.930412 2083.81732,728.84314 2083.82081,728.755929 L2088.2792,617.312956 C2088.32396,616.194028 2089.24407,615.30999 2090.36389,615.30999 Z'

    if np.isnan(lastVar2) == 0:
        shownLastVar2 = round(lastVar2, 1)
    else:
        shownLastVar2 = 0

    fig2 = pn.indicators.Gauge(
        name=name, value=shownLastVar2, bounds=(0, Var2Max), format='{value} ' + Var2udm,
        colors=[(Var2Minus / Var2Max, 'red'), (Var2Plus / Var2Max, 'gold'), (1, 'green')], annulus_width=5,
        custom_opts={"pointer": {"itemStyle": {"color": "black"}, 'icon': pointer_path}, "value": {"color": "black"},
                     "axisLabel": {
                         "color": 'black', "fontSize": 10,
                     },
                     "detail": {"color": value_color, "fontSize": 14},
                     "radius": '90%', "nan_format": "-"}
    )

    fig2.width = 250
    fig2.height = 250

    fig2.save('graph2.html', embed=True, embed_json=True)

    GaugUp = open('graph2.html', 'r')

    GaugeScript = GaugUp.read()

    GaugeData = {"HTML": GaugeScript, "ledColor": ledColor}

    return GaugeData


def createVar3Gauge(Data):

    name = Data["Var3name"]
    Var3Max = Data["Var3Max"]
    Var3udm = Data["udm"]
    Var3Minus = Data["MeanVar3"] - Data["DevVar3"]
    Var3Plus = Data["MeanVar3"] + Data["DevVar3"]
    lastVar3 = Data["lastVar3"]
    Plant = Data["Plant"]

        # Var2Max = Data["Var2Max"] / 1000
        # QMinus = QMinus / 1000
        # QPlus = QPlus

    if lastVar3 < Var3Minus:
        ledColor = "led-red"
        value_color ="red"
    elif lastVar3 > Var3Plus:
        ledColor = "led-green"
        value_color ="green"

    else:
        ledColor = "led-yellow"
        value_color ="black"
    pointer_path = 'path://M2090.36389,615.30999 L2090.36389,615.30999 C2091.48372,615.30999 2092.40383,616.194028 2092.44859,617.312956 L2096.90698,728.755929 C2097.05155,732.369577 2094.2393,735.416212 2090.62566,735.56078 C2090.53845,735.564269 2090.45117,735.566014 2090.36389,735.566014 L2090.36389,735.566014 C2086.74736,735.566014 2083.81557,732.63423 2083.81557,729.017692 C2083.81557,728.930412 2083.81732,728.84314 2083.82081,728.755929 L2088.2792,617.312956 C2088.32396,616.194028 2089.24407,615.30999 2090.36389,615.30999 Z'

    if np.isnan(lastVar3) == 0:
        shownLastVar3 = round(lastVar3, 1)
    else:
        shownLastVar3 = 0

    fig2 = pn.indicators.Gauge(
        name=name, value=shownLastVar3, bounds=(0, Var3Max), format='{value} '+Var3udm,
        colors=[(Var3Minus/Var3Max, 'red'), (Var3Plus/Var3Max, 'gold'), (1, 'green')], annulus_width=5,
        custom_opts={"pointer": {"itemStyle": {"color": "black"}, 'icon': pointer_path}, "value": {"color": "black"},
                     "axisLabel": {
                         "color": 'black', "fontSize": 10,
                     },
                     "detail": {"color": value_color, "fontSize": 14},
                     "radius": '90%'}
    )

    fig2.width = 250
    fig2.height = 250

    fig2.save('graph3.html', embed=True, embed_json=True)

    GaugUp = open('graph3.html', 'r')

    GaugeScript = GaugUp.read()

    GaugeData = {"HTML": GaugeScript, "ledColor": ledColor}

    return GaugeData


