import json
import os
from datetime import datetime
from typing import Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import tweepy
from pydantic import BaseModel
from pytz import timezone

from province_bar_chart import draw_bar_chart


class AggregatedData(BaseModel):
    # anyErrorTps: str = None
    # anyLaporTps: str
    # anyPendingTps: str
    # idLokasi: str
    name: str
    pas1: int
    pas2: int
    pas3: int
    totalCompletedTps: int
    # totalErrorTps: int
    # totalJagaTps: int
    # totalLaporTps: int
    # totalPendingTps: int
    totalTps: int
    # updateTs: int


class Result(BaseModel):
    names: List[str]
    id: str
    aggregated: Dict[str, List[AggregatedData]]
    numWrites: int
    lastCachedTs: int


class Data(BaseModel):
    result: Result


request_json = {
    "data": {
        "id": "",
    },
}

response = requests.get("https://kp24-fd486.et.r.appspot.com/h?id=")
try:
    r = requests.post(
        "https://us-central1-kp24-fd486.cloudfunctions.net/hierarchy2",
        json=request_json,
    )
    r.raise_for_status()
    response = r
except requests.exceptions.HTTPError as e:
    print(e)

data = Data(**response.json())

from datetime import datetime

ts = int("1284101485")

last_cached = datetime.fromtimestamp(data.result.lastCachedTs / 1000)
last_cached = last_cached.astimezone(timezone("Asia/Jakarta"))
last_cached = last_cached.strftime("%d %b %Y %H:%M:%S %Z")
print(f"Last cached: {last_cached}")

total_pas1 = 0
total_pas2 = 0
total_pas3 = 0
total_percentage_pas1 = 0
total_percentage_pas2 = 0
total_percentage_pas3 = 0

total_processed_tps = 0
total_tps = 0

total_pas1_win20 = 0
total_pas2_win20 = 0
total_pas3_win20 = 0
name_pas1_win20 = []
name_pas2_win20 = []
name_pas3_win20 = []

answer = "Sepertinya iya 🤔"

d = {
    "PROVINSI": [],
    "Paslon 1": [],
    "Paslon 2": [],
    "Paslon 3": [],
    "Pemenang": [],
    "Δ sebaran suara Paslon 2": [],
}

bar_chart_paslon_data = []
bar_chart_provinsi_data = []


class BarChartData(BaseModel):
    selisih: float
    paslon_votes: List[float]
    provinces: str


bar_chart_data = []

for name, aggregated_data in data.result.aggregated.items():
    for data in aggregated_data:
        total_pas1 += data.pas1
        total_pas2 += data.pas2
        total_pas3 += data.pas3
        total = data.pas1 + data.pas2 + data.pas3
        if total == 0:
            continue

        total_processed_tps += data.totalCompletedTps
        total_tps += data.totalTps

        percentage_pas1 = (data.pas1 / total) * 100
        percentage_pas2 = (data.pas2 / total) * 100
        percentage_pas3 = (data.pas3 / total) * 100
        print(
            f"{data.name}: {percentage_pas1:.2f}% {percentage_pas2:.2f}% {percentage_pas3:.2f}%"
        )

        pas1_3_percentages = [percentage_pas1, percentage_pas3]
        pas1_3_percentages.sort(reverse=True)

        selisih = round(percentage_pas2 - pas1_3_percentages[0], 2)

        winner = "N/A"
        if (
            percentage_pas1 > percentage_pas2 + 20
            and percentage_pas1 > percentage_pas3 + 20
        ):
            winner = "Paslon 1"
            total_pas1_win20 += 1
            name_pas1_win20.append(data.name)
            print(f"\t{data.name}: Paslon 1 menang 20% lebih banyak")

        if (
            percentage_pas2 > percentage_pas1 + 20
            and percentage_pas2 > percentage_pas3 + 20
        ):
            winner = "Paslon 2"
            total_pas2_win20 += 1
            name_pas2_win20.append(data.name)
            print(f"\t{data.name}: Paslon 2 menang {selisih}% lebih banyak")

            chart_data = BarChartData(
                selisih=selisih,
                paslon_votes=[
                    round(percentage_pas1, 2),
                    round(percentage_pas2, 2),
                    round(percentage_pas3, 2),
                ],
                provinces=f"{data.name} ({selisih}%)",
            )
            bar_chart_data.append(chart_data)
            # bar_chart_paslon_data.insert(
            #     0,
            #     [
            #         round(percentage_pas1, 2),
            #         round(percentage_pas2, 2),
            #         round(percentage_pas3, 2),
            #     ],
            # )
            # bar_chart_provinsi_data.insert(0, f"{data.name} ({selisih}%)")

        if (
            percentage_pas3 > percentage_pas1 + 20
            and percentage_pas3 > percentage_pas2 + 20
        ):
            winner = "Paslon 3"
            total_pas3_win20 += 1
            name_pas3_win20.append(data.name)
            print(f"\t{data.name}: Paslon 3 menang 20% lebih banyak")

        d["PROVINSI"].append(data.name)
        d["Paslon 1"].append(f"{percentage_pas1:.2f}%")
        d["Paslon 2"].append(f"{percentage_pas2:.2f}%")
        d["Paslon 3"].append(f"{percentage_pas3:.2f}%")
        d["Pemenang"].append(winner)
        d["Δ sebaran suara Paslon 2"].append(selisih)

        print()

print("========================================\n")

print(
    f"""Paslon 1 menang 20% di {total_pas1_win20} provinsi: {name_pas1_win20}\n
Paslon 2 menang 20% di {total_pas2_win20} provinsi: {name_pas2_win20}\n
Paslon 3 menang 20% di {total_pas3_win20} provinsi: {name_pas3_win20}\n"""
)

print("========================================\n")

total = total_pas1 + total_pas2 + total_pas3
total_percentage_pas1 = (total_pas1 / total) * 100
total_percentage_pas2 = (total_pas2 / total) * 100
total_percentage_pas3 = (total_pas3 / total) * 100
total_percentage_tps = (total_processed_tps / total_tps) * 100

if total_percentage_pas1 > 50 and total_pas1_win20 >= 20:
    answer = "Sepertinya tidak 🤔"
elif total_percentage_pas2 > 50 and total_pas2_win20 >= 20:
    answer = "Sepertinya tidak 🤔"
elif total_percentage_pas3 > 50 and total_pas3_win20 >= 20:
    answer = "Sepertinya tidak 🤔"

bar_chart_data.sort(key=lambda x: x.selisih)
fig = draw_bar_chart(
    bar_chart_data, last_cached, total_processed_tps, total_tps, total_percentage_tps
)
fig.write_html("sebaran_paslon2.html")
fig.write_image("sebaran_paslon2.png", width=1920, height=1080)

mapbox_accesstoken = os.getenv("MAPBOX_ACCESS_TOKEN")

df = pd.DataFrame(data=d)

with open("data/small/Provinsi.json") as file:
    provinces = json.load(file)

for feature in provinces["features"]:
    feature["properties"]["PROVINSI"] = str.upper(feature["properties"]["PROVINSI"])

fig = px.choropleth_mapbox(
    df,
    geojson=provinces,
    color="Pemenang",
    locations="PROVINSI",
    featureidkey="properties.PROVINSI",
    center={"lat": -2.5, "lon": 120},
    hover_data=["Paslon 1", "Paslon 2", "Paslon 3", "Δ sebaran suara Paslon 2"],
    mapbox_style="carto-positron",
    zoom=4,
)

fig.update_layout(
    mapbox_accesstoken=mapbox_accesstoken,
    mapbox_style="light",
    title=go.layout.Title(
        text=f"""Pemenang 20% sebaran suara per provinsi
<br><sup>Dari <a href="https://kawalpemilu.org">https://kawalpemilu.org</a> versi {last_cached}, progress: {total_processed_tps:,} dari {total_tps:,} TPS ({total_percentage_tps:.2f}%)</sup>""",
        xref="paper",
        x=0,
    ),
    legend_title_text="",
)
fig.write_html("index.html")
fig.write_image("pemenang_20persen.png", width=1920, height=1080)

# fig = px.choropleth_mapbox(
#     df,
#     geojson=provinces,
#     color="Δ sebaran suara Paslon 2",
#     color_continuous_scale="Bluered",
#     locations="PROVINSI",
#     featureidkey="properties.PROVINSI",
#     center={"lat": -2.5, "lon": 120},
#     hover_data=["Paslon 1", "Paslon 2", "Paslon 3"],
#     mapbox_style="carto-positron",
#     zoom=4,
# )

# fig.update_layout(
#     mapbox_accesstoken=mapbox_accesstoken,
#     mapbox_style="light",
#     title=go.layout.Title(
#         text=f"""Selisih sebaran suara Paslon 2 per provinsi<br><sup>Dari <a href="https://kawalpemilu.org">https://kawalpemilu.org</a> versi {last_cached}, progress: {total_processed_tps:,} dari {total_tps:,} TPS ({total_percentage_tps:.2f}%)</sup>""",
#         xref="paper",
#         x=0,
#     ),
# )
# fig.write_html("sebaran_paslon2.html")
# fig.write_image("sebaran_paslon2.png", width=1920, height=1080)

print("========================================\n")


newStatus = f"""Dari kawalpemilu.org @KawalPemilu_org

Paslon 1: {total_pas1:,} ({total_percentage_pas1:.2f}%) menang 20% di {total_pas1_win20} provinsi
Paslon 2: {total_pas2:,} ({total_percentage_pas2:.2f}%) menang 20% di {total_pas2_win20} provinsi
Paslon 3: {total_pas3:,} ({total_percentage_pas3:.2f}%) menang 20% di {total_pas3_win20} provinsi

Total TPS: {total_processed_tps:,} dari {total_tps:,} ({total_percentage_tps:.2f}%)"""
print(newStatus)
print()
print("========================================\n")

consumer_key = os.getenv("TWITTER_CONSUMER_API_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")

auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret, access_token, access_token_secret
)
api = tweepy.API(auth=auth, wait_on_rate_limit=True)

pemenang_20persen_media = api.media_upload("pemenang_20persen.png")
sebaran_paslon2 = api.media_upload("sebaran_paslon2.png")

client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
)
response = client.create_tweet(
    text=newStatus,
    media_ids=[pemenang_20persen_media.media_id, sebaran_paslon2.media_id],
)

print(f"https://twitter.com/user/status/{response.data['id']}")
