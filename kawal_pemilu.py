import os
from typing import Dict, List

import requests
import tweepy
from pydantic import BaseModel


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

        if (
            percentage_pas1 > percentage_pas2 + 20
            and percentage_pas1 > percentage_pas3 + 20
        ):
            total_pas1_win20 += 1
            name_pas1_win20.append(data.name)
            print(f"\t{data.name}: Paslon 1 menang 20% lebih banyak")

        if (
            percentage_pas2 > percentage_pas1 + 20
            and percentage_pas2 > percentage_pas3 + 20
        ):
            total_pas2_win20 += 1
            name_pas2_win20.append(data.name)
            print(f"\t{data.name}: Paslon 2 menang 20% lebih banyak")

        if (
            percentage_pas3 > percentage_pas1 + 20
            and percentage_pas3 > percentage_pas2 + 20
        ):
            total_pas3_win20 += 1
            name_pas3_win20.append(data.name)
            print(f"\t{data.name}: Paslon 3 menang 20% lebih banyak")

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

client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
)

response = client.create_tweet(text=newStatus)
print(f"https://twitter.com/user/status/{response.data['id']}")
