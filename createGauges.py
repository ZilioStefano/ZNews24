import numpy as np
import panel as pn
import pandas as pd
pn.extension('echarts')


def expected_eta(last_var2, plant, last_var3):

    if plant == "SA3":

        filename = "rendimentoReale" + plant + ".csv"
        curva_rendimento = pd.read_csv(filename)

        q_teo = curva_rendimento["QOut"]
        if plant != "TF" and plant != "SA3":
            q_teo = q_teo / 1000

        eta_teo = curva_rendimento["etaOut"]
        eta_dev = curva_rendimento["devEta"]

        # cerco i valori più vicini last Q

        i = 0
        while last_var2 > q_teo.iloc[i]:
            i = i + 1

        if i != 0:
            eta_aspettato = (eta_teo[i - 1] + eta_teo[i]) / 2
            dev_aspettato = 0.5 * np.sqrt(eta_dev[i - 1] ** 22 + eta_dev[i] ** 2)
        else:
            eta_aspettato = (eta_teo[i] + eta_teo[i]) / 2
            dev_aspettato = 0.5 * np.sqrt(eta_dev[i] ** 2 + eta_dev[i] ** 2)

        eta_min = eta_aspettato - dev_aspettato
        eta_max = eta_aspettato + dev_aspettato

    else:
        
        if plant != "TF" and plant != "SA3" and plant != "SCN":
            last_var2 = last_var2 * 1000
        
        mean_file = "MeanEta" + plant + ".csv"
        dev_file = "DevEta" + plant + ".csv"

        curva_rendimento = pd.read_csv(mean_file, header=None)
        dev_rendimento = pd.read_csv(dev_file, header=None)

        asse_var2 = curva_rendimento.iloc[0, 1:]
        asse_var3 = curva_rendimento.iloc[1:, 0]

        # cerco i valori più vicini last Q
        
        i = 0
        var2test = asse_var2.iloc[i]
        print(len(asse_var2))

        while last_var2 > var2test and i < len(asse_var2)-1:
            print(str(i))
            i = i + 1
            var2test = asse_var2.iloc[i]

        j = 0
        var3test = asse_var3.iloc[j]
        
        if np.isnan(last_var3):
            last_var3 = 0
        final_j = 1
        while last_var3 > var3test and j < len(asse_var3):
            j = j + 1
            if j >= len(asse_var3):
                final_j = j - 1
                var3test = asse_var3.iloc[final_j]

            else:
                final_j = j
                var3test = asse_var3.iloc[final_j]

        eta_aspettato = curva_rendimento.iloc[final_j, i]
        if np.isnan(eta_aspettato):
            eta_aspettato = np.mean([curva_rendimento.iloc[final_j - 1, i], curva_rendimento.iloc[final_j + 1, i],
                                     curva_rendimento.iloc[final_j, i - 1], curva_rendimento.iloc[final_j, i + 1]])

        dev_aspettato = dev_rendimento.iloc[final_j, i]

        eta_min = eta_aspettato - dev_aspettato
        eta_max = eta_aspettato + dev_aspettato

    return eta_aspettato, eta_min, eta_max


def create_power_gauge(data):

    last_power = float(data[0])
    power_max = float(data[1])
    power_minus = float(data[2] - data[3])
    power_plus = float(data[2] + data[3])

    if last_power < power_minus:
        led_color = "led-red"
        value_color = "red"

    elif last_power > power_plus:
        led_color = "led-green"
        value_color = "green"

    else:
        led_color = "led-yellow"
        value_color = "black"

    pointer_path = ('path://M2090.36389,615.30999 L2090.36389,615.30999 C2091.48372,615.30999 2092.40383,616.194028 '
                    '2092.44859,617.312956 L2096.90698,728.755929 C2097.05155,732.369577 2094.2393,735.416212 '
                    '2090.62566,735.56078 C2090.53845,735.564269 2090.45117,735.566014 2090.36389,735.566014 '
                    'L2090.36389,735.566014 C2086.74736,735.566014 2083.81557,732.63423 2083.81557,729.017692 '
                    'C2083.81557,728.930412 2083.81732,728.84314 2083.82081,728.755929 L2088.2792,617.312956 '
                    'C2088.32396,616.194028 2089.24407,615.30999 2090.36389,615.30999 Z')

    if np.isnan(last_power) == 0:
        shown_power = round(last_power)
    else:
        shown_power = 0

    fig = pn.indicators.Gauge(
        name="P", value=shown_power, bounds=(0, power_max), format='{value} kW',
        colors=[(power_minus / power_max, 'red'), (power_plus / power_max, 'gold'), (1, 'green')],
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

    gauge_up = open('graph.html', 'r')
    gauge_script = gauge_up.read()

    gauge_data = {"HTML": gauge_script, "ledColor": led_color}

    return gauge_data


def create_eta_gauge(data):

    last_eta = 100 * data[0]
    eta_max = data[1]
    eta_minus = 100 * (data[2] - data[3])
    eta_plus = 100 * (data[2] + data[3])
    
    name = data["etaName"]
    if last_eta < eta_minus:
        led_color = "led-red"
        value_color = "red"
    elif last_eta > eta_plus:
        led_color = "led-green"
        value_color = "green"
    else:
        led_color = "led-yellow"
        value_color = "black"

    pointer_path = ('path://M2090.36389,615.30999 L2090.36389,615.30999 C2091.48372,615.30999 2092.40383,616.194028 '
                    '2092.44859,617.312956 L2096.90698,728.755929 C2097.05155,732.369577 2094.2393,735.416212 '
                    '2090.62566,735.56078 C2090.53845,735.564269 2090.45117,735.566014 2090.36389,735.566014 '
                    'L2090.36389,735.566014 C2086.74736,735.566014 2083.81557,732.63423 2083.81557,729.017692 '
                    'C2083.81557,728.930412 2083.81732,728.84314 2083.82081,728.755929 L2088.2792,617.312956 '
                    'C2088.32396,616.194028 2089.24407,615.30999 2090.36389,615.30999 Z')

    if np.isnan(last_eta) == 0:
        shown_eta = round(last_eta, 1)
    else:
        shown_eta = 0

    fig = pn.indicators.Gauge(
        name=name, value=shown_eta, bounds=(0, eta_max), format='{value} %',
        colors=[(eta_minus / eta_max, 'red'), (eta_plus / eta_max, 'gold'), (1, 'green')], annulus_width=5,
        custom_opts={"pointer": {"itemStyle": {"color": "black"}, 'icon': pointer_path}, "value": {"color": "black"},
                     "axisLabel": {"color": 'black', "fontSize": 10}, "detail": {"color": value_color, "fontSize": 14},
                     "radius": '90%', "nan_format": "-"}
    )

    fig.width = 250
    fig.height = 250
    fig.save('graph.html')  # , embed=True, embed_json=True)

    gauge_up = open('graph.html', 'r')

    gauge_script = gauge_up.read()

    # DatiRef = {"etaRef": etaAspettato, "devEta": etaAspettato-etaMinus}

    gauge_data = {"HTML": gauge_script, "ledColor": led_color}

    return gauge_data


def create_var2_gauge(data):

    name = data["Var2name"]
    var2max = data["Var2Max"]
    var2udm = data["udm"]
    var2minus = data["MeanVar2"] - data["DevVar2"]
    var2plus = data["MeanVar2"] + data["DevVar2"]
    last_var2 = data["lastVar2"]

    if last_var2 < var2minus:
        led_color = "led-red"
        value_color = "red"

    elif last_var2 > var2plus:
        led_color = "led-green"
        value_color = "green"

    else:
        led_color = "led-yellow"
        value_color = "black"

    pointer_path = ('path://M2090.36389,615.30999 L2090.36389,615.30999 C2091.48372,615.30999 2092.40383,616.194028 '
                    '2092.44859,617.312956 L2096.90698,728.755929 C2097.05155,732.369577 2094.2393,735.416212 '
                    '2090.62566,735.56078 C2090.53845,735.564269 2090.45117,735.566014 2090.36389,735.566014 '
                    'L2090.36389,735.566014 C2086.74736,735.566014 2083.81557,732.63423 2083.81557,729.017692 '
                    'C2083.81557,728.930412 2083.81732,728.84314 2083.82081,728.755929 L2088.2792,617.312956 '
                    'C2088.32396,616.194028 2089.24407,615.30999 2090.36389,615.30999 Z')

    if np.isnan(last_var2) == 0:
        shown_last_var2 = round(last_var2, 1)
    else:
        shown_last_var2 = 0

    fig2 = pn.indicators.Gauge(
        name=name, value=shown_last_var2, bounds=(0, var2max), format='{value} ' + var2udm,
        colors=[(var2minus / var2max, 'red'), (var2plus / var2max, 'gold'), (1, 'green')], annulus_width=5,
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

    gauge_up = open('graph2.html', 'r')

    gauge_script = gauge_up.read()

    gauge_data = {"HTML": gauge_script, "ledColor": led_color}

    return gauge_data

def create_var3_gauge(data):

    name = data["Var3name"]
    var3max = data["Var3Max"]
    var3udm = data["udm"]
    var3minus = data["MeanVar3"] - data["DevVar3"]
    var3plus = data["MeanVar3"] + data["DevVar3"]
    last_var3 = data["lastVar3"]

    if last_var3 < var3minus:
        led_color = "led-red"
        value_color = "red"
    elif last_var3 > var3plus:
        led_color = "led-green"
        value_color = "green"

    else:
        led_color = "led-yellow"
        value_color = "black"
    pointer_path = ('path://M2090.36389,615.30999 L2090.36389,615.30999 C2091.48372,615.30999 2092.40383,616.194028 '
                    '2092.44859,617.312956 L2096.90698,728.755929 C2097.05155,732.369577 2094.2393,735.416212 '
                    '2090.62566,735.56078 C2090.53845,735.564269 2090.45117,735.566014 2090.36389,735.566014 '
                    'L2090.36389,735.566014 C2086.74736,735.566014 2083.81557,732.63423 2083.81557,729.017692 '
                    'C2083.81557,728.930412 2083.81732,728.84314 2083.82081,728.755929 L2088.2792,617.312956 '
                    'C2088.32396,616.194028 2089.24407,615.30999 2090.36389,615.30999 Z')

    if np.isnan(last_var3) == 0:
        shown_last_var3 = round(last_var3, 1)
    else:
        shown_last_var3 = 0

    fig2 = pn.indicators.Gauge(
        name=name, value=shown_last_var3, bounds=(0, var3max), format='{value} ' + var3udm,
        colors=[(var3minus / var3max, 'red'), (var3plus / var3max, 'gold'), (1, 'green')], annulus_width=5,
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

    gauge_up = open('graph3.html', 'r')

    gauge_script = gauge_up.read()

    gauge_data = {"HTML": gauge_script, "ledColor": led_color}

    return gauge_data
