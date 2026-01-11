from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# データ保存用の簡易データベース（本番ではDBを使用）
DATA_FILE = 'locations.json'

def load_locations():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_location(location):
    locations = load_locations()
    locations.append(location)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/save-location', methods=['POST'])
def save_location_api():
    try:
        data = request.json
        
        # 日本の位置情報かチェック（簡易版）
        lat = data.get('latitude')
        lng = data.get('longitude')
        
        # 日本国内チェック（緯度経度の範囲）
        # 日本の大まかな範囲：北緯20°〜46°、東経122°〜154°
        is_in_japan = (20 <= lat <= 46) and (122 <= lng <= 154)
        
        if not is_in_japan:
            return jsonify({
                'success': False,
                'error': '日本国内からのアクセスのみ対応しています'
            }), 400
        
        location_data = {
            'latitude': lat,
            'longitude': lng,
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'ip': request.remote_addr
        }
        
        save_location(location_data)
        
        return jsonify({
            'success': True,
            'message': '位置情報を保存しました',
            'location': location_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/admin/locations')
def view_locations():
    """管理者用：取得した位置情報を表示"""
    locations = load_locations()
    return jsonify({
        'count': len(locations),
        'locations': locations
    })

@app.route('/dashboard')
def dashboard():
    """クライアント2用ダッシュボード"""
    locations = load_locations()
    return render_template('dashboard.html', locations=locations)

if __name__ == '__main__':
    # テンプレートフォルダ設定
    app.template_folder = '.'
    app.run(debug=True, port=5000)
