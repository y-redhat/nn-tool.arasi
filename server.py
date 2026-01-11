from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # 全オリジンを許可

# データ保存用ファイル
DATA_FILE = 'locations.json'

def save_location(location_data):
    """位置情報を保存"""
    locations = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            locations = json.load(f)
    
    locations.append(location_data)
    
    with open(DATA_FILE, 'w') as f:
        json.dump(locations, f, indent=2)
    
    return locations

@app.route('/')
def home():
    return """
    <h1>位置情報システム</h1>
    <p>クライアント1: <a href="/client1">/client1</a></p>
    <p>クライアント2: <a href="/client2">/client2</a></p>
    <p>API: <a href="/api/locations">/api/locations</a></p>
    """

@app.route('/client1')
def client1():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>クライアント1</title></head>
    <body>
        <h1>位置情報取得</h1>
        <button onclick="getLocation()">位置情報を取得</button>
        <div id="result"></div>
        
        <script>
        function getLocation() {
            document.getElementById("result").innerHTML = "取得中...";
            
            if (!navigator.geolocation) {
                document.getElementById("result").innerHTML = "位置情報非対応";
                return;
            }
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const data = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    };
                    
                    // サーバーに送信
                    fetch("/api/save-location", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify(data)
                    })
                    .then(res => res.json())
                    .then(result => {
                        document.getElementById("result").innerHTML = 
                            "成功！3秒後にダウンロード開始...";
                        
                        // ダウンロード
                        setTimeout(() => {
                            window.location.href = "https://example.com/sample.pdf";
                        }, 3000);
                    });
                },
                function(error) {
                    document.getElementById("result").innerHTML = "エラー: " + error.message;
                }
            );
        }
        </script>
    </body>
    </html>
    '''

@app.route('/client2')
def client2():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>クライアント2</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            #map { height: 400px; background: #eee; margin: 20px 0; }
            .location { border: 1px solid #ccc; padding: 10px; margin: 5px 0; }
        </style>
    </head>
    <body>
        <h1>位置情報ダッシュボード</h1>
        <button onclick="loadData()">データ読み込み</button>
        <div id="map">地図表示エリア</div>
        <div id="locations"></div>
        
        <script>
        function loadData() {
            fetch("/api/locations")
                .then(res => res.json())
                .then(data => {
                    let html = "<h2>取得済み位置情報 (" + data.length + "件)</h2>";
                    data.forEach(loc => {
                        html += `
                            <div class="location">
                                <strong>${new Date(loc.timestamp).toLocaleString()}</strong><br>
                                緯度: ${loc.latitude}, 経度: ${loc.longitude}
                            </div>
                        `;
                    });
                    document.getElementById("locations").innerHTML = html;
                });
        }
        
        // 初回読み込み
        loadData();
        </script>
    </body>
    </html>
    '''

@app.route('/api/save-location', methods=['POST'])
def api_save_location():
    data = request.json
    data['timestamp'] = request.json.get('timestamp') or os.times().system
    save_location(data)
    return jsonify({"status": "success"})

@app.route('/api/locations')
def api_get_locations():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return jsonify(json.load(f))
    return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
