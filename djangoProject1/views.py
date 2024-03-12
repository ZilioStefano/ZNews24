import pandas as pd
from django.shortcuts import render
from ftplib import FTP
import csv
from retrieveData import read_plant_data, create_plots, create_gauges, create_label


def read_alarm(plant):

    ftp = FTP("192.168.10.211", timeout=120)
    ftp.login('ftpdaticentzilio', 'Sd2PqAS.We8zBK')
    ftp.cwd('/dati/Database_Produzione')
    g_file = open("AlarmStatesBeta.csv", "wb")
    ftp.retrbinary('RETR AlarmStatesBeta.csv', g_file.write)
    g_file.close()

    stato_allarmi = csv.DictReader(open("AlarmStatesBeta.csv"))

    for row in stato_allarmi:
        stato_allarmi = row
    if plant == "SCN":
        curr_alarm = {"SCN1": stato_allarmi["SCN1"], "SCN2": stato_allarmi["SCN2"]}

    else:
        curr_alarm = stato_allarmi[plant]

    return curr_alarm


def retrieve_data(plant, plant_state):

    data = read_plant_data(plant)
    data["Plant state"] = plant_state
    data["Plant"] = plant

    plots = create_plots(data)
    gauges = create_gauges(data)
    label = create_label(data)

    if plant_state == "A":
        page_color = "IndianRed"
    else:
        page_color = "#e2f5ef"

    html_data = {
        "Production": plots["Production plot"]["Graph"], "Eta": plots["Eta plot"]["Graph"],
        "GaugeEta": gauges["Eta"]["HTML"], "LedEta": gauges["Eta"]["ledColor"], "GaugePower": gauges["Power"]["HTML"],
        "LedPower": gauges["Power"]["ledColor"], "Gauge2": gauges["Var2"]["HTML"], "Led2": gauges["Var2"]["ledColor"],
        "Gauge3": gauges["Var3"]["HTML"], "Led3": gauges["Var3"]["ledColor"],
        "Label": label, "pagecolor": page_color
    }

    return html_data


def switch_plant():

    plants = ["SA3", "TF", "ST", "PAR", "CST", "PG"]
    n = len(plants)

    index_df = pd.read_csv('current index.csv')
    index_df["index"] = (index_df['index'][0] + 1) % n
    index_df.to_csv("current index.csv", index=False)
    curr_plant = plants[index_df["index"][0]]

    return curr_plant


def set_template(plant):

    if (plant == "TF" or plant == "ST" or plant == "PAR" or plant == "SA3" or plant == "PG" or plant == "CST"
            or plant == "SCN" or plant == "RUB"):
        template = "mainPage.html"

    else:
        template = ""

    return template


def main(request):

    curr_plant = switch_plant()
    print(curr_plant)
    plant_state = read_alarm(curr_plant)
    template = set_template(curr_plant)
    html_data = retrieve_data(curr_plant, plant_state)

    return render(request, template, context=html_data)
