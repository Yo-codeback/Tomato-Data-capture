# -*- coding: utf-8 -*-
import os
import json
import requests
import threading
import logging
from datetime import datetime

from time import sleep


DATA_FILE = "taipei_data.json"

def fetch_data_for_taipei():
    """抓取台北二市場的番茄-牛番茄數據，並在 CMD 顯示"""
    url = "https://data.moa.gov.tw/api/v1/AgriProductsTransType/"
    today = datetime.now()
    minguo_date = f"{today.year - 1911:03}.{today.month:02}.{today.day:02}"
    params = {"Start_time": minguo_date, "End_time": minguo_date, "CropCode": "FJ3"}

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    if any(item["交易日期"] == minguo_date for item in existing_data):
        print("\n⚠ 今日數據已存在，直接顯示")
        display_data(existing_data)
        return

    print("\n🔍 正在抓取今日台北二市場數據...")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get("Data"):
            print("\n⚠ 今日為休市日，無交易數據")
            return

        filtered_data = [
            {
                "交易日期": item["TransDate"],
                "市場名稱": item["MarketName"],
                "平均價": item["Avg_Price"],
                "交易量": item["Trans_Quantity"]
            }
            for item in data["Data"]
            if item["CropCode"] == "FJ3" and item["MarketName"] == "台北二"
        ]

        if filtered_data:
            existing_data.extend(filtered_data)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)
            print("\n✅ 今日數據已存入！")

        display_data(filtered_data)

    except requests.exceptions.RequestException:
        print("\n❌ 錯誤：無法獲取資料！")

def display_data(data):
    """在 CMD 顯示番茄數據"""
    if not data:
        print("\n⚠ 今日為休市日，無交易數據")
        return

    print("\n📊 今日台北二市場 番茄-牛番茄 數據")
    print("=" * 50)
    for item in data:
        print(f"📅 日期：{item['交易日期']}")
        print(f"🏬 市場：{item['市場名稱']}")
        print(f"💰 平均價：{item['平均價']} 元/公斤")
        print(f"📦 交易量：{item['交易量']} 公斤")
        print("🔔 今日數據如上! 喜歡今天的價格嗎??")
        print("-" * 50)


def periodic_fetch():
    """每 30 秒抓取一次資料"""
    while True:
        fetch_data_for_taipei()
        sleep(30)  # 每 30 秒執行一次

if __name__ == "__main__":
    fetch_data_for_taipei()  # 啟動時抓取一次數據
    threading.Thread(target=periodic_fetch, daemon=True).start()  # 背景定時更新數據
   