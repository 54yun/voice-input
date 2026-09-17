#!/bin/bash
# 安装手机语音输入自启动服务

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$HOME/.config/systemd/user"

# 复制voice.py到用户目录
mkdir -p "$HOME/voice-input"
cp "$SCRIPT_DIR/voice.py" "$HOME/voice-input/"
chmod +x "$HOME/voice-input/voice.py"

# 创建服务文件
mkdir -p "$TARGET_DIR"
cat > "$TARGET_DIR/voice-input.service" << 'EOF'
[Unit]
Description=手机语音输入服务
After=graphical.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/yun/voice-input/voice.py
Restart=always
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
EOF

# 重新加载systemd
systemctl --user daemon-reload

# 启用自启动
systemctl --user enable voice-input.service
systemctl --user start voice-input.service

echo "✅ 自启动已配置"
echo "  文件: ~/voice-input/voice.py"
echo "  手机访问: http://$(hostname -I | awk '{print $1}'):8899"
