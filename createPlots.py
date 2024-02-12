from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd


def createEtaPlot(Data):

    State = Data["Plant state"]

    if State == "W":
        lineColor = 'grey'
    else:
        lineColor = 'orange'

    t = Data["Timeline"]["t"]
    t = pd.to_datetime(t)
    eta = 100 * Data["Timeline"]["Eta"]
    Yesterday = datetime.now() - timedelta(days=1)

    fig1 = px.line(None, t, eta, template="ggplot2")
    fig1.update_traces(line_color=lineColor)
    fig1.update_layout(height=300, width=1700, title_text="Rendimenti", margin=dict(r=165))
    tMax = datetime.now()
    tMin = tMax - timedelta(hours=24)
    fig1.update_layout({'xaxis': {'range': [tMin, tMax]}})
    fig1.update_layout({'yaxis': {'range': [min(eta[t >= tMin]), max(max(eta[t>=tMin]), 1)]}})
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
    PMin = min(P)
    PMax = max(P)

    if PlantType == "Hydro":
        Var2 = Data["Timeline"]["Q"]

    else:
        Var2 = Data["Timeline"]["Q"]

    Var2Min = min(Var2)
    Var2Max = max(Var2)
    tMax = datetime.now()
    tMin = tMax - timedelta(hours=24)
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
    subfig.layout.yaxis2.color = "blue"
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
    else:
        Title = "San Teodoro"

    TitleChSize = 30
    subfig.update_layout(template=template, height=400, width=1700, title_text=Title, title_font=dict(size=TitleChSize))

    subfig.layout.yaxis2.color = "blue"
    subfig.update_layout({'xaxis': {'range': [tMin, tMax]}})
    subfig.update_layout({'yaxis': {'range': [min(0, PMin), max(Data["PMax"], PMax)]}})
    subfig.update_layout({'yaxis2': {'range': [min(0, Var2Min), max(Data["Var2Max"], Var2Max)]}})

    GraphData = subfig.to_html('graph.html')
    PlotData = {"Graph": GraphData}

    return PlotData
