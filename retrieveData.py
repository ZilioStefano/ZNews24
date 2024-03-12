from ftplib import FTP
import pandas as pd
from createPlots import createProdPlot, createEtaPlot, createCSTPlot
from createGauges import create_eta_gauge, create_power_gauge, create_var2_gauge, create_var3_gauge
from num2string import convertNumber as cvN
import numpy as np
import csv
import json


def create_label(data):

    last24_data = data["last24hStat"]
    energy_last24, dummy = cvN(last24_data["Energy"][0], "Energy", "HTML", data["Plant"])

    if np.isnan(last24_data["etaMean"][0]):
        eta_last24 = ""
    else:
        eta_last24 = str(round(100 * last24_data["etaMean"][0], 1)) + " %"

    this_month_data = data["thisMonthStat"]
    this_year_data = data["thisYearStat"]
    plant = data["Plant"]

    if plant == "SCN":

        av24 = (str(round(100 * np.mean([last24_data["Availability Inv 1"][0], last24_data["Availability Inv 2"][0]]), 1))
                + " %")
        av_this_month = str(round(100 * np.mean([this_month_data["Availability Inv 1"][0],
                                                 this_month_data["Availability Inv 2"][0]]), 1)) + " %"
        av_this_year = str(round(100 * np.mean([this_year_data["Availability Inv 1"][0],
                                                this_year_data["Availability Inv 2"][0]]), 1)) + " %"
    else:
        av24 = str(round(100 * last24_data["Availability"][0], 1)) + " %"
        av_this_month = str(round(100 * this_month_data["Availability"][0], 1)) + " %"
        av_this_year = str(round(100 * this_year_data["Availability"][0], 1)) + " %"

    yeald_last24, dummy = cvN(last24_data["Resa"][0], "Money", "HTML", data["Plant"])

    energy_this_month, dummy = cvN(this_month_data["Energy"][0], "Energy", "HTML", data["Plant"])
    eta_this_month = str(round(100 * this_month_data["etaMean"][0], 1)) + " %"
    yeld_this_month, dummy = cvN(this_month_data["Resa"][0], "Money", "HTML", data["Plant"])

    energy_this_year, dummy = cvN(this_year_data["Energy"][0], "Energy", "HTML", data["Plant"])
    eta_this_year = str(round(100 * this_year_data["etaMean"][0], 1)) + " %"
    yeld_this_year, dummy = cvN(this_year_data["Resa"][0], "Money", "HTML", data["Plant"])

    if plant == "SCN" or plant == "RUB":
        yeald_last24 = yeald_last24 + " RID"
        yeld_this_month = yeld_this_month + " RID"
        yeld_this_year = yeld_this_year + " RID"

    label = {"last24h": {"Energy": energy_last24, "Eta": eta_last24, "Av": av24, "Yeald": yeald_last24},
             "thisMonth": {"Energy": energy_this_month, "Eta": eta_this_month, "Av": av_this_month, "Yeald": yeld_this_month},
             "thisYear": {"Energy": energy_this_year, "Eta": eta_this_year, "Av": av_this_year, "Yeald": yeld_this_year}}

    return label


def create_gauges(data):

    if len(data["last24hTL"]) == 0:

        last_var2 = float('NaN')
        last_var3 = float('NaN')

    else:
        if data["PlantType"] == "PV":

            last_var2 = data["last24hTL"]["I"].iloc[-1]
            last_var3 = data["last24hTL"]["TMod"].iloc[-1]

        else:

            last_var2 = data["last24hTL"]["Q"].iloc[-1]
            last_var3 = data["last24hTL"]["Bar"].iloc[-1]

    if np.isnan(last_var2):
        last_var2 = 0
        
    data_in = data["DatiGauge"]
    eta_data = data_in["Eta"]
    # EtaData["Plant"] = Data["Plant"]
    eta_data["etaName"] = data["etaName"]

    eta_gauge_data = create_eta_gauge(eta_data)

    power_data = data_in["Power"]
    power_gauge_data = create_power_gauge(power_data)

    if data["Plant"] != "TF" and data["Plant"] != "SA3" and data["Plant"] != "SCN":
        data_q = last_var2 * 1000
    else:
        data_q = last_var2

    data_gauge = {
        "lastVar2": data_q, "Var2Max": data["Var2"]["Max"], "udm": data["Var2"]["udm"], "Var2name": data["Var2"]["name"],
        "MeanVar2": data["Var2"]["Media"], "DevVar2": data["Var2"]["Dev"], "Plant": data["Plant"]
    }

    var2_gauge_data = create_var2_gauge(data_gauge)

    data_gauge = {"lastVar3": last_var3, "Var3Max": data["Var3"]["Max"], "udm": data["Var3"]["udm"],
                 "Var3name": data["Var3"]["name"], "MeanVar3": data["Var3"]["Media"], "DevVar3": data["Var3"]["Dev"],
                 "Plant": data["Plant"]}

    var3_gauge_data = create_var3_gauge(data_gauge)

    gauge_data = {"Eta": eta_gauge_data, "Var2": var2_gauge_data, "Power": power_gauge_data, "Var3": var3_gauge_data}

    return gauge_data


def create_plots(data):

    plant = data["Plant"]
    df_year_tl = data["thisYearTL"]
    plant_type = data["PlantType"]

    if plant != "TF" and plant_type == "Hydro":
        df_year_tl["Q"] = df_year_tl["Q"] * 1000

    if plant != "CST":
        data_plot = {"Plant": plant, "Timeline": df_year_tl, "Plant state": data["Plant state"],
                    "Plant type": data["PlantType"], "PMax": data["PMax"], "Var2Max": data["Var2"]["Max"],
                    "Var2udm": data["Var2"]["udm"]}
        production_plot = createProdPlot(data_plot)
        
    else:
        data_plot = {"Plant": plant, "Timeline": df_year_tl, "Plant state": data["Plant state"],
                    "Plant type": data["PlantType"], "PMax": data["PMax"], "Var2Max": data["Var2"]["Max"]}
        production_plot = createCSTPlot(data_plot)

    eta_plot = createEtaPlot(data_plot)

    plots = {"Production plot": production_plot, "Eta plot": eta_plot}

    return plots


def read_plant_data(plant):

    ftp = FTP("192.168.10.211", timeout=120)
    ftp.login('ftpdaticentzilio', 'Sd2PqAS.We8zBK')
    udm_var2 = ""

    if plant == "ST":
        ftp.cwd('/dati/San_Teodoro')
        plant_type = "Hydro"
        power_max = 260
        var2max = 80
        var2media = 69.4
        var2dev = 15
        var3media = 27.1
        var3dev = 0.5
        var3max = 40
        pn = power_max
        udm_var2 = "l/s"
        folder = "San_Teodoro"

    elif plant == "TF":
        ftp.cwd('/dati/Torrino_Foresta')
        plant_type = "Hydro"
        power_max = 400
        var2max = 3
        var2media = 0.9787
        var2dev = 0.983
        var3media = 1.41
        var3dev = 0.04
        var3max = 2
        pn = power_max
        udm_var2 = "m\u00b3/s"
        folder = "Torrino_Foresta"

    elif plant == "PG":
        ftp.cwd('/dati/ponte_giurino')
        plant_type = "Hydro"
        var2max = 80
        var2media = 12
        var2dev = 15
        var3media = 31.5
        var3dev = 0.9
        power_max = 250
        var3max = 50
        pn = power_max
        udm_var2 = "l/s"
        folder = "ponte_giurino"

    elif plant == "SA3":
        
        ftp.cwd('/dati/SA3')
        plant_type = "Hydro"
        var2max = 80
        var2media = 9.77
        var2dev = 9.76
        power_max = 250
        var3media = 1.5
        var3max = 3
        var3dev = 1
        pn = power_max
        udm_var2 = "m\u00b3/s"
        folder = "SA3"

    elif plant == "CST":

        ftp.cwd('/dati/San_Teodoro')
        plant_type = "Hydro"
        power_max = 260 + 100
        var2max = 110
        var2media = 26 + 69.4
        var2dev = np.sqrt(15 ** 2 + 15 ** 2)
        var3media = (27.1 + 26.9) / 2
        var3dev = 0.5 * np.sqrt(0.5 ** 2 + 0.5 ** 2)
        var3max = 36
        pn = power_max
        udm_var2 = "l/s"
        folder = "San_Teodoro"

    elif plant == "SCN":

        ftp.cwd('/dati/SCN')
        plant_type = "PV"
        power_max = 930
        var2max = 1000
        var2media = 390
        var2dev = 333
        var3media = 27
        var3dev = 14
        var3max = 70
        pn = 927
        folder = "SCN"

    elif plant == "RUB":
        ftp.cwd('/dati/Rubino')
        plant_type = "PV"
        power_max = 998
        var2max = 1300
        var2media = 469
        var2dev = 327
        var3max = 1300
        var3media = 19
        var3dev = 16
        pn = 997
        folder = "Rubino"

    else:
        ftp.cwd('/dati/San_Teodoro')
        plant_type = "Hydro"
        power_max = 100
        var2max = 30
        var2media = 26
        var2dev = 6
        var3media = 26.9
        var3dev = 0.5
        var3max = 36
        pn = power_max
        udm_var2 = "l/s"
        folder = "San_Teodoro"

    if plant_type == "Hydro":

        name_var2 = "Q"
        udm_var3 = "barg"
        name_var3 = "h"
        eta_name = "\u03b7"
    else:
        udm_var2 = "W/m\u00b2"
        name_var2 = "I"
        udm_var3 = "°C"
        name_var3 = "T"
        eta_name = "PR"

    last24file = plant + "last24hTL.csv"

    g_file = open(last24file, "wb")
    ftp.retrbinary("RETR " + last24file, g_file.write)
    g_file.close()
    df24h_tl = pd.read_csv(last24file)

    df24h_tl["PMax"] = power_max
    df24h_tl["Var2Max"] = var2max
    df24h_tl["Var3Max"] = var3max

    this_year_file = plant + "YearTL.csv"

    g_file = open(this_year_file, "wb")
    ftp.retrbinary("RETR " + this_year_file, g_file.write)
    g_file.close()
    this_year_tl = pd.read_csv(this_year_file)

    this_year_tl["PMax"] = power_max
    this_year_tl["Var2Max"] = var2max
    this_year_tl["Var3Max"] = var3max

    last24_statfile = plant + "last24hStat.csv"

    g_file = open(last24_statfile, "wb")
    ftp.retrbinary("RETR " + last24_statfile, g_file.write)
    g_file.close()
    last24stat = pd.read_csv(last24_statfile)

    last24stat["PMax"] = power_max
    last24stat["Var2Max"] = var2max
    last24stat["Var3Max"] = var3max

    this_month_stat_file = plant + "MonthStat.csv"

    g_file = open(this_month_stat_file, "wb")
    ftp.retrbinary("RETR " + this_month_stat_file, g_file.write)
    g_file.close()
    this_month_stat = pd.read_csv(this_month_stat_file)

    this_month_stat["PMax"] = power_max
    this_month_stat["Var2Max"] = var2max
    this_month_stat["Var3Max"] = var3max

    this_year_statfile = plant + "YearStat.csv"

    g_file = open(this_year_statfile, "wb")
    ftp.retrbinary("RETR " + this_year_statfile, g_file.write)
    g_file.close()
    this_year_stat = pd.read_csv(this_year_statfile)

    this_year_stat["PMax"] = power_max
    this_year_stat["Var2Max"] = var2max
    this_year_stat["Var3Max"] = var3max

    filename = plant+"_dati_gauge.csv"
    ftp.cwd('/dati/'+folder)
    g_file = open(filename, "wb")
    ftp.retrbinary('RETR ' + filename, g_file.write)
    g_file.close()

    dati_gauge = pd.read_csv(filename)

    ftp.close()

    data = {
        "last24hTL": df24h_tl, "thisYearTL": this_year_tl, "last24hStat": last24stat, "thisMonthStat": this_month_stat,
        "thisYearStat": this_year_stat, "PlantType": plant_type, "PMax": power_max,
        "Var2": {"Max": var2max, "udm": udm_var2, "name": name_var2, "Media": var2media, "Dev": var2dev},
        "Var3": {"Max": var3max, "Media": var3media, "Dev": var3dev, "udm": udm_var3, "name": name_var3},
        "etaName": eta_name, "PN": pn, "DatiGauge": dati_gauge,
    }

    return data
