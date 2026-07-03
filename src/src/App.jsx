import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { initializeApp } from 'firebase/app'
import { getDatabase, ref, onValue } from 'firebase/database'
import './App.css'

const firebaseConfig = {
  apiKey: "AIzaSyBIRqPgfKX...",  // 不要（REST APIを使用）
  databaseURL: "https://tenki-makaki-default-rtdb.firebaseio.com"
}

const app = initializeApp(firebaseConfig)
const db = getDatabase(app)

export default function App() {
  const [weatherData, setWeatherData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Firebase から最新24時間のデータを取得
    const dbRef = ref(db, 'weather/weathernews')
    
    onValue(dbRef, (snapshot) => {
      const data = snapshot.val()
      if (data) {
        // データを時系列でソート
        const sorted = Object.entries(data)
          .map(([date, hourData]) => {
            return Object.entries(hourData || {}).map(([hour, values]) => ({
              time: `${date} ${hour}:00`,
              latest: values.latest,
              '1h前': values['1h_ago'],
              '2h前': values['2h_ago']
            }))
          })
          .flat()
          .sort((a, b) => new Date(a.time) - new Date(b.time))
          .slice(-24)  // 最新24時間のみ

        setWeatherData(sorted)
      }
      setLoading(false)
    })
  }, [])

  if (loading) {
    return <div className="container"><p>読み込み中...</p></div>
  }

  return (
    <div className="container">
      <h1>加古川の天気予報集約</h1>
      <p className="subtitle">ウェザーニュース - 時間別降水量（mm）</p>

      {weatherData.length > 0 ? (
        <div className="chart-wrapper">
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={weatherData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="time" 
                angle={-45}
                textAnchor="end"
                height={100}
              />
              <YAxis label={{ value: '降水量（mm）', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="latest" stroke="#ff6b6b" name="現在" strokeWidth={2} />
              <Line type="monotone" dataKey="1h前" stroke="#4ecdc4" name="1時間前" strokeWidth={2} />
              <Line type="monotone" dataKey="2h前" stroke="#95e1d3" name="2時間前" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <p>データが利用可能ではありません</p>
      )}
    </div>
  )
}
