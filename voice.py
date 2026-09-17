#!/usr/bin/env python3
"""
手机语音输入Web服务器
用法：python3 voice.py
手机打开 http://电脑IP:8899
"""

import json
import subprocess
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler

HOST = "0.0.0.0"
PORT = 8899

HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>语音输入</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding: 40px 20px 200px 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 24px;
            width: 100%;
            max-width: 380px;
        }
        h1 { text-align: center; color: #333; margin-bottom: 16px; font-size: 22px; }
        #status {
            text-align: center;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 16px;
            font-size: 14px;
            font-weight: 600;
        }
        .ok { background: #d4edda; color: #155724; }
        .err { background: #f8d7da; color: #721c24; }
        .sending { background: #cce5ff; color: #004085; }
        .waiting { background: #fff3cd; color: #856404; }
        textarea {
            width: 100%;
            height: 120px;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            resize: none;
        }
        textarea:focus { outline: none; border-color: #667eea; }
        .tips {
            margin-top: 16px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 10px;
            font-size: 13px;
            color: #666;
            line-height: 1.6;
        }
        .tips strong { color: #333; }
        .history { margin-top: 16px; border-top: 1px solid #eee; padding-top: 12px; }
        .history h3 { font-size: 13px; color: #999; margin-bottom: 8px; }
        .history-item {
            background: #f8f9fa;
            padding: 8px 10px;
            border-radius: 6px;
            margin-bottom: 6px;
            font-size: 12px;
            color: #666;
            cursor: pointer;
            word-break: break-all;
        }
        .history-item:active { background: #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 语音输入</h1>
        <div id="status" class="waiting">就绪</div>
        <textarea id="textInput" placeholder="粘贴文字后自动发送..."></textarea>
        <div class="tips">
            <strong>使用方法：</strong><br>
            1. 手机用讯飞/豆包语音输入<br>
            2. 识别后复制文字<br>
            3. 打开此页面，粘贴到文本框<br>
            4. 自动发送到电脑剪贴板<br>
            5. 电脑上 Ctrl+V 粘贴
        </div>
        <div class="history">
            <h3>最近发送</h3>
            <div id="historyList"></div>
        </div>
    </div>
    <script>
        let lastText = '';
        let sendTimer = null;
        let history = JSON.parse(localStorage.getItem('voiceHistory') || '[]');
        document.getElementById('textInput').addEventListener('input', function() {
            const text = this.value.trim();
            if (text && text !== lastText) {
                clearTimeout(sendTimer);
                sendTimer = setTimeout(() => {
                    sendText(text);
                    lastText = text;
                }, 3000);
            }
        });
        async function sendText(text) {
            document.getElementById('status').textContent = '⏳ 发送中...';
            document.getElementById('status').className = 'sending';
            try {
                const res = await fetch('/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: text })
                });
                if (res.ok) {
                    document.getElementById('status').textContent = '✅ 已发送 - 电脑上 Ctrl+V 粘贴';
                    document.getElementById('status').className = 'ok';
                    history.unshift(text);
                    if (history.length > 10) history.pop();
                    localStorage.setItem('voiceHistory', JSON.stringify(history));
                    updateHistoryUI();
                    document.getElementById('textInput').value = '';
                    lastText = '';
                } else {
                    throw new Error('失败');
                }
            } catch (e) {
                document.getElementById('status').textContent = '❌ 发送失败';
                document.getElementById('status').className = 'err';
            }
            setTimeout(() => {
                document.getElementById('status').textContent = '就绪';
                document.getElementById('status').className = 'waiting';
            }, 2000);
        }
        function updateHistoryUI() {
            document.getElementById('historyList').innerHTML = history.slice(0, 5).map((t, i) =>
                '<div class="history-item" onclick="reuse(' + i + ')">' + (t.length > 30 ? t.substring(0, 30) + '...' : t) + '</div>'
            ).join('');
        }
        function reuse(i) {
            document.getElementById('textInput').value = history[i];
            document.getElementById('textInput').dispatchEvent(new Event('input'));
        }
        window.onload = updateHistoryUI;
    </script>
</body>
</html>'''

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def copy_to_clipboard(text):
    try:
        p = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
        p.communicate(text.encode('utf-8'))
        return True
    except Exception as e:
        print(f"[错误] {e}")
        return False

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(HTML.encode())
    
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        data = json.loads(body)
        text = data.get("content", "")
        if text:
            copy_to_clipboard(text)
            print(f"[已复制] {text[:50]}...")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    local_ip = get_local_ip()
    print("=" * 50)
    print("  📱 手机语音输入 → 电脑剪贴板")
    print("=" * 50)
    print()
    print(f"  手机访问: http://{local_ip}:{PORT}")
    print(f"  电脑访问: http://127.0.0.1:{PORT}")
    print()
    print("  按 Ctrl+C 停止")
    print("=" * 50)
    HTTPServer((HOST, PORT), Handler).serve_forever()
