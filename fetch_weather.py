import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import pytz
import re

WEATHERNEWS_URL = "https://weathernews.jp/onebox/tenki/hyogo/28210/"
FIREBASE_DB_URL = "https://tenki-makaki-default-rtdb.firebaseio.com"

jst = pytz.timezone('Asia/Tokyo')
now_jst = datetime.now(jst)

print(f"取得時刻: {now_jst.strftime('%Y-%m-%d %H:%M:%S JST')}")

try:
    response = requests.get(WEATHERNEWS_URL, timeout=10)
    response.encoding = 'utf-8'
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1時間ごとの <ul> を取得
        hourly_lists = soup.find_all('ul', id=re.compile(r'wx_.*hour'))
        
        print(f"見つかった時間単位ブロック数: {len(hourly_lists)}")
        
        # すべてのデータを一度に整理
        all_data = {}
        
        # Firebase にデータを保存
        for idx, ul in enumerate(hourly_lists):
            try:
                # 時刻情報を取得
                time_li = ul.find('li', class_='time')
                time_text = ""
                if time_li:
                    time_text = time_li.get_text(strip=True)
                
                # 降水量データを取得
                rain_li = ul.find('li', class_='rain')
                value = 0
                
                if rain_li:
                    p_tag = rain_li.find('p')
                    if p_tag:
                        text = p_tag.get_text(strip=True)
                        match = re.search(r'[\d.]+', text)
                        value = float(match.group()) if match else 0
                
                print(f"  [{idx}] 時刻: {time_text}, 降水量: {value} mm")
                
                # データを保存
                data = {
                    "latest": value,
                    "timestamp": now_jst.isoformat(),
                    "source": "weathernews"
                }
                
                # 時刻情報から日付と時間を抽出して保存
                if time_text:
                    firebase_url = f"{FIREBASE_DB_URL}/weather/weathernews/{now_jst.strftime('%Y-%m-%d')}/{time_text}.json"
                    firebase_response = requests.put(firebase_url, json=data, timeout=10)
                            
            except Exception as e:
                print(f"  [{idx}] エラー: {e}")
        
        print(f"\n✅ 取得・保存完了（{len(hourly_lists)}時間分）")
    else:
        print(f"❌ ページの取得失敗: {response.status_code}")
        
except Exception as e:
    print(f"❌ エラーが発生しました: {e}")
