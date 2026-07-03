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
        rain_elements = soup.find_all('li', class_='rain')
        rainfall_data = []
        
        print(f"見つかった rain 要素数: {len(rain_elements)}")
        
        for idx, element in enumerate(rain_elements[:3]):
            try:
                p_tag = element.find('p')
                if p_tag:
                    text = p_tag.get_text(strip=True)
                    match = re.search(r'[\d.]+', text)
                    if match:
                        value = float(match.group())
                    else:
                        value = 0
                    rainfall_data.append(value)
                    print(f"  [{idx}] 降水量: {value} mm")
            except Exception as e:
                print(f"  [{idx}] エラー: {e}")
                rainfall_data.append(0)
        
        if rainfall_data:
            data = {
                "latest": rainfall_data[0],
                "1h_ago": rainfall_data[1] if len(rainfall_data) > 1 else None,
                "2h_ago": rainfall_data[2] if len(rainfall_data) > 2 else None,
                "timestamp": now_jst.isoformat(),
                "source": "weathernews"
            }
            
            firebase_url = f"{FIREBASE_DB_URL}/weather/weathernews/{now_jst.strftime('%Y-%m-%d/%H')}.json"
            firebase_response = requests.put(firebase_url, json=data, timeout=10)
            
            print(f"\n✅ Firebase 保存完了")
            print(f"   URL: {firebase_url}")
            print(f"   Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print("❌ 降水量データが取得できませんでした")
    else:
        print(f"❌ ページの取得失敗: {response.status_code}")
        
except Exception as e:
    print(f"❌ エラーが発生しました: {e}")
