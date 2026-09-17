# 手机语音输入 → 电脑剪贴板

手机语音输入文字，自动发送到电脑剪贴板，电脑 `Ctrl+V` 粘贴。

## 功能

- 手机无需安装任何 App
- 支持所有语音输入法（讯飞、豆包等）
- 粘贴后自动发送到电脑
- 历史记录保存在浏览器本地
- 零依赖，纯 Python 标准库

## 使用

### 手动运行

```bash
python3 voice.py
```

手机打开 `http://电脑IP:8899`

### 安装自启动

```bash
./install.sh
```

服务安装后开机自动后台运行。

## 管理

```bash
systemctl --user start voice-input    # 启动
systemctl --user stop voice-input     # 停止
systemctl --user restart voice-input  # 重启
systemctl --user status voice-input   # 状态
systemctl --user disable voice-input  # 取消自启动
```

## 流程

1. 手机用讯飞/豆包语音输入
2. 识别后复制文字
3. 手机打开 `http://电脑IP:8899`
4. 粘贴到文本框，3秒后自动发送
5. 电脑上 `Ctrl+V` 粘贴

## 依赖

- Python 3
- xclip（Debian 系统自带）

## 许可

MIT License
