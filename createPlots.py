from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def createEtaPlot(Data):
    State = Data["Plant state"]

    if State == "W":
        lineColor = 'grey'
    else:
        lineColor = 'orange'

    t = Data["Timeline"]["t"]
    t = pd.to_datetime(t)

    tMax = datetime.now()
    tMin = tMax - timedelta(days=1)

    tNew = []
    etaNew = []
    tCurr = tMin

    if len(t) > 0:

        eta = 100 * Data["Timeline"]["Eta"]

    else:

        while tCurr <= tMax:
            tNew.append(tCurr)
            etaNew.append(float('NaN'))
            tCurr = tCurr + timedelta(hours=1)

        eta = etaNew
        t = tNew

        t = pd.to_datetime(t)
        eta = np.array(eta)

    fig1 = px.line(None, t, eta, template="ggplot2")
    fig1.update_traces(line_color=lineColor)
    if Data["Plant"] == "CST":
        right_margin = 225
    else:
        right_margin = 110

    fig1.update_layout(
        height=500, width=1500,
        title_text="Rendimenti",
        margin=dict(l=10, r=right_margin, t=70, b=10),
        font=dict(
            size=20,  # Set the font size here
            color="RebeccaPurple"),
    )

    fig1.update_layout({'xaxis': {'range': [tMin, tMax]}})
    if Data["Plant"] == "SCN":
        etaMax = 150
    else:
        etaMax = 100

    if len(eta[t >= tMin]) > 0 and not np.isnan(eta).any():
        fig1.update_layout({'yaxis': {
            'range': [min(eta[(t >= tMin) & (eta < etaMax)]), max(max(eta[(t >= tMin) & (eta < etaMax)]), etaMax)]}})

    fig1.layout.yaxis.title = "Rendimento [%]"
    fig1.layout.xaxis.title = ""

    GraphData = fig1.to_html('graph.html')
    PlotData = {"Graph": GraphData}

    return PlotData


def createProdPlot(Data):

    State = Data["Plant state"]
    PlantType = Data["Plant type"]
    Plant = Data["Plant"]

    if State == "W":
        AreaColor = "grey"
        lineColor = "grey"

    else:
        if PlantType == "PV":
            lineColor = 'orange'
            AreaColor = 'green'
        else:
            lineColor = 'blue'
            AreaColor = 'green'

    template = "ggplot2"

    t = Data["Timeline"]["t"]
    # t = pd.to_datetime(t)
    P = Data["Timeline"]["P"]

    tMax = datetime.now()
    tMin = tMax - timedelta(hours=24)

    tNew = []
    PNew = []
    QNew = []
    tCurr = tMin

    if len(t) > 0:

        if PlantType == "Hydro":
            Var2 = Data["Timeline"]["Q"]

        else:
            Var2 = Data["Timeline"]["I"]

    else:

        while tCurr <= tMax:
            tNew.append(tCurr)
            PNew.append(float('NaN'))
            QNew.append(float('NaN'))
            tCurr = tCurr + timedelta(hours=1)
        P = PNew
        t = tNew
        Var2 = QNew

    PMin = min(P)
    PMax = max(P)

    Var2Min = min(Var2)
    Var2Max = max(Var2)

    fig1 = px.area(None, t, P, template=template, range_x=[tMin, tMax])
    fig1.update_traces(yaxis="y1", line_color=AreaColor)

    fig2 = px.line(None, t, Var2, template=template, range_x=[tMin, tMax])
    fig2.update_layout({'xaxis': {'range': [tMin, tMax]}})
    fig2.update_traces(yaxis="y2", line_color=lineColor)

    subfig = make_subplots(specs=[[{"secondary_y": True}]])
    subfig.add_traces(list(fig1.data + fig2.data))

    subfig.layout.xaxis.title = ""
    subfig.layout.yaxis.title = "Potenza [kW]"
    subfig.layout.yaxis.color = "green"
    subfig.layout.yaxis2.color = lineColor
    subfig.layout.yaxis2.title = Data["Var2udm"]

    if Plant == "TF":
        # subfig.layout.yaxis2.title = "Portata [m^3/s]"
        Title = "Torrino Foresta"

    elif Plant == "PAR":
        Title = "Partitore"

    elif Plant == "PG":
        Title = "Ponte Giurino"
    elif Plant == "CST":
        Title = "Condotta San Teodoro"
    elif Plant == "SA3":
        Title = "SA3"
    elif Plant == "SCN":
        Title = "SCN Pilota"

    elif Plant == "RUB":
        Title = "Rubino"
    else:
        Title = "San Teodoro"

    TitleChSize = 30
    subfig.update_layout(template=template,
                         height=500, width=1500,
                         title_text=Title,
                         title_font=dict(size=TitleChSize),
                         margin=dict(l=10, r=10, t=70, b=10),
                         font=dict(
                             size=20,  # Set the font size here
                             color="RebeccaPurple"
                         ),
                         )

    # subfig.layout.yaxis2.color = "blue"
    subfig.update_layout({'xaxis': {'range': [tMin, tMax]}})
    subfig.update_layout({'yaxis': {'range': [min(0, PMin), max(Data["PMax"], PMax)]}})
    subfig.update_layout({'yaxis2': {'range': [min(0, Var2Min), max(Data["Var2Max"], Var2Max)]}})

    GraphData = subfig.to_html('graph.html')
    PlotData = {"Graph": GraphData}

    return PlotData


def createCSTPlot(Data):
    State = Data["Plant state"]
    PlantType = Data["Plant type"]
    Plant = Data["Plant"]

    if State == "W":
        lineColor = "grey"

    else:
        if PlantType == "PV":
            lineColor = 'orange'
        else:
            lineColor = 'blue'

    template = "ggplot2"

    t = Data["Timeline"]["t"]
    # t = pd.to_datetime(t)
    P = Data["Timeline"]["P"]

    tMax = datetime.now()
    tMin = tMax - timedelta(hours=24)

    tNew = []
    PNew = []
    QNew = []
    tCurr = tMin

    if len(t) > 0:

        if PlantType == "Hydro":
            Var2 = Data["Timeline"]["Q"]

        else:
            Var2 = Data["Timeline"]["Q"]

    else:

        while tCurr <= tMax:
            tNew.append(tCurr)
            PNew.append(float('NaN'))
            PSTNew.append(float('NaN'))
            PPARNew.append(float('NaN'))
            QNew.append(float('NaN'))
            tCurr = tCurr + timedelta(hours=1)
            
        P = PNew
        t = tNew
        Var2 = QNew

    PMin = min(P)
    PMax = max(P)

    Var2Min = min(Var2)
    Var2Max = max(Var2)

    fig1 = px.area(Data["Timeline"], x="t", y=["PST", "PPAR"], labels={"ST": "San Teodoro", "PAR": "Partitore"},
                   range_x=[tMin, tMax])

    fig2 = px.line(None, t, Var2, template=template, range_x=[tMin, tMax])
    fig2.update_layout({'xaxis': {'range': [tMin, tMax]}})
    fig2.update_traces(yaxis="y2", line_color=lineColor)

    subfig = make_subplots(specs=[[{"secondary_y": True}]])
    subfig.add_traces(list(fig1.data + fig2.data))

    subfig.layout.xaxis.title = ""
    subfig.layout.yaxis.title = "Potenza [kW]"
    subfig.layout.yaxis2.color = lineColor
    subfig.layout.yaxis2.title = "Portata [l/s]"

    if Plant == "TF":
        subfig.layout.yaxis2.title = "Portata [m^3/s]"
        Title = "Torrino Foresta"

    elif Plant == "PAR":
        Title = "Partitore"

    elif Plant == "PG":
        Title = "Ponte Giurino"
    elif Plant == "CST":
        Title = "Condotta San Teodoro"
    elif Plant == "SA3":
        Title = "SA3"
    elif Plant == "SCN":
        Title = "SCN Pilota"
    elif Plant == "RUB":
        Title = "Rubino"
    else:
        Title = "San Teodoro"

    TitleChSize = 30
    subfig.update_layout(template=template,
                         height=500, width=1800,
                         title_text=Title,
                         title_font=dict(size=TitleChSize),
                         margin=dict(l=10, r=10, t=70, b=10),
                         font=dict(
                             size=20,  # Set the font size here
                             color="RebeccaPurple"
                         ),
                         )

    subfig.layout.yaxis2.color = "blue"
    subfig.update_layout({'xaxis': {'range': [tMin, tMax]}})
    subfig.update_layout({'yaxis': {'range': [min(0, PMin), max(Data["PMax"], PMax)]}})
    subfig.update_layout({'yaxis2': {'range': [min(0, Var2Min), max(Data["Var2Max"], Var2Max)]}})

    GraphData = subfig.to_html('graph.html')
    PlotData = {"Graph": GraphData}

    return PlotData
