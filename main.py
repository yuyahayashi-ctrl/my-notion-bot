import os
import requests
import threading
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# 3つの鍵を環境変数から読み込む
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
DIFY_API_KEY = os.environ["DIFY_API_KEY"]

# アプリを初期化
app = App(token=SLACK_BOT_TOKEN)

# Difyに質問を投げる共通の処理
def ask_dify(text, user_id, say):
    try:
        response = requests.post(
            "https://api.dify.ai/v1/chat-messages",
            headers={
                "Authorization": f"Bearer {DIFY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "inputs": {},
                "query": text,
                "user": user_id,
                "response_mode": "blocking",
            }
        )
        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "（答えが見つかりませんでした）")
            say(answer)
        else:
            say(f"Difyエラー: {response.text}")
    except Exception as e:
        say(f"システムエラー: {str(e)}")

# ① みんなのチャンネルで名前を呼ばれた時の処理
@app.event("app_mention")
def handle_mentions(event, say):
    ask_dify(event["text"], event["user"], say)

# ② DM（1対1）で直接話しかけられた時の処理
@app.event("message")
def handle_message(event, say):
    # ボット自身が送ったメッセージには反応しないようにする
    if event.get("subtype") is None:
        ask_dify(event["text"], event["user"], say)

# --- Renderのポートエラー回避用ダミーサーバー ---
def run_dummy_server():
    os.system("python3 -m http.server 10000")

if __name__ == "__main__":
    threading.Thread(target=run_dummy_server, daemon=True).start()
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
