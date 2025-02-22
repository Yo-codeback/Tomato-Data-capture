from fastapi import FastAPI
import json
import requests
from datetime import datetime
import uvicorn
import time
import itertools
import threading
import sys

app = FastAPI()

# 🔄 動態載入數據
def load_data():
    with open("taipei_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/data")
async def get_data():
    """返回台北二市場的番茄數據"""
    return load_data()

# 🎬 CMD 動畫（讓查詢更有感覺！）
def animated_loading():
    for c in itertools.cycle(['.  ', '.. ', '...']):
        sys.stdout.write(f"\r🔍 正在查詢中 {c}")
        sys.stdout.flush()
        time.sleep(0.1)
        if stop_animation:
            break

def fetch_data_for_taipei():
    """抓取番茄數據並存入 JSON，保留超美 CMD 輸出"""
    global stop_animation
    stop_animation = False
    animation_thread = threading.Thread(target=animated_loading)
    animation_thread.start()

    url = "https://data.moa.gov.tw/api/v1/AgriProductsTransType/"
    today = datetime.now()
    minguo_date = f"{today.year - 1911:03}.{today.month:02}.{today.day:02}"
    params = {"Start_time": minguo_date, "End_time": minguo_date, "CropCode": "FJ3"}

    print("\n==================================================")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        stop_animation = True
        animation_thread.join()

        if not data.get("Data"):
            print("\n⚠ 今日為休市日，無交易數據 😴")
            print("-" * 50)  
            return

        filtered_data = [
            {
                "交易日期": item["TransDate"],
                "市場名稱": item["MarketName"],
                "平均價": item["Avg_Price"],
                "交易量": item["Trans_Quantity"]
            }
            for item in data["Data"]
            if item["CropCode"] == "FJ3" and item["MarketName"] == "台北二" and item["CropName"] != "休市"
        ]

        if filtered_data:
            with open("taipei_data.json", "w", encoding="utf-8") as f:
                json.dump(filtered_data, f, ensure_ascii=False, indent=4)

            print("\n📅 今日日期：", minguo_date)
            print("🔍 查詢 台北二市場 番茄價格")
            print("==================================================")
            print("🟩 查詢完成 🟩")
            print(f"\n📌 日期：{filtered_data[0]['交易日期']}")
            print(f"🏬 市場：{filtered_data[0]['市場名稱']}")
            print(f"💰 平均價：{filtered_data[0]['平均價']} 元/公斤")
            print(f"📦 交易量：{filtered_data[0]['交易量']} 公斤")
            print(f"🎯 ✅ 資料已更新完成！")
        else:
            print("\n⚠ 今日為休市日，無交易數據")
            print("-" * 50)
    except requests.exceptions.RequestException as e:
        stop_animation = True
        animation_thread.join()
        print("\n❌ 錯誤：無法獲取資料！")
        print("-" * 50)

def auto_fetch_data():
    """每隔 3 分鐘自動抓取一次數據"""
    while True:
        fetch_data_for_taipei()
        time.sleep(180)  # 3 分鐘更新一次

if __name__ == "__main__":
    fetch_data_for_taipei()  # 啟動時先抓一次數據
    threading.Thread(target=auto_fetch_data, daemon=True).start()  # 每 3 分鐘自動更新數據
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")  # 靜音大部分輸出
