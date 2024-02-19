from __future__ import annotations

import os
import random
import time

import requests
import tweepy

response = requests.get(
    "https://sirekap-obj-data.kpu.go.id/wilayah/pemilu/ppwp/0.json",
)
regions = {}
for region in response.json():
    regions[region["kode"]] = region

# time.sleep(0.5)
# response = requests.get("https://sirekap-obj-data.kpu.go.id/pemilu/ppwp.json")
# candidates = {}
# for key, value in response.json().items():
#     candidates[key] = value
# print(candidates)
# print("========================================")

# Hard coded candidates and their id
# Paslon 1 => 100025
# Paslon 2 => 100026
# Paslon 3 => 100027

total_pas1 = 0
total_pas2 = 0
total_pas3 = 0
total_percentage_pas1 = 0
total_percentage_pas2 = 0
total_percentage_pas3 = 0

total_pas1_win20 = 0
total_pas2_win20 = 0
total_pas3_win20 = 0
name_pas1_win20 = []
name_pas2_win20 = []
name_pas3_win20 = []

time.sleep(0.3)
response = requests.get("https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp.json")
for region_kode, vote_result in response.json()["table"].items():
    if (
        "100025" not in vote_result
        or "100026" not in vote_result
        or "100027" not in vote_result
    ):
        continue

    region_name = regions[region_kode]["nama"]
    total_pas1 += vote_result["100025"]
    total_pas2 += vote_result["100026"]
    total_pas3 += vote_result["100027"]
    total = total_pas1 + total_pas2 + total_pas3

    percentage_pas1 = (total_pas1 / total) * 100
    percentage_pas2 = (total_pas2 / total) * 100
    percentage_pas3 = (total_pas3 / total) * 100

    print(
        f"{region_name}: {percentage_pas1:.2f}% {percentage_pas2:.2f}% {percentage_pas3:.2f}%"
    )

    if (
        percentage_pas1 > percentage_pas2 + 20
        and percentage_pas1 > percentage_pas3 + 20
    ):
        total_pas1_win20 += 1
        name_pas1_win20.append(region_name)
        print(f"\t{region_name}: Paslon 1 menang 20% lebih banyak")

    if (
        percentage_pas2 > percentage_pas1 + 20
        and percentage_pas2 > percentage_pas3 + 20
    ):
        total_pas2_win20 += 1
        name_pas2_win20.append(region_name)
        print(f"\t{region_name}: Paslon 2 menang 20% lebih banyak")

    if (
        percentage_pas3 > percentage_pas1 + 20
        and percentage_pas3 > percentage_pas2 + 20
    ):
        total_pas3_win20 += 1
        name_pas3_win20.append(region_name)
        print(f"\t{region_name}: Paslon 3 menang 20% lebih banyak")

    print()

print("========================================\n")

total = total_pas1 + total_pas2 + total_pas3
total_percentage_pas1 = (total_pas1 / total) * 100
total_percentage_pas2 = (total_pas2 / total) * 100
total_percentage_pas3 = (total_pas3 / total) * 100

total_processed_tps = response.json()["progres"]["progres"]
total_tps = response.json()["progres"]["total"]
total_percentage_tps = (total_processed_tps / total_tps) * 100

newStatus = f"""Dari pemilu2024.kpu.go.id @KPU_ID

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

time.sleep(random.randint(1, 3))
response = client.create_tweet(text=newStatus)
print(f"https://twitter.com/user/status/{response.data['id']}")
