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

# メンションされたら反応する設定
@app.event("app_mention")
def handle_mentions(event, say):
    text = event["text"]
    user_id = event["user"]
    
    try:
        # Difyに質問を投げる
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

# --- Renderのポートエラーを回避するためのダミーサーバー設定 ---
def run_dummy_server():
    # Renderが期待する10000番ポートで簡易サーバーを起動
    os.system("python3 -m http.server 10000")

if __name__ == "__main__":
    # ダミーサーバーを別スレッドで起動
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    # Slackボットを起動
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
