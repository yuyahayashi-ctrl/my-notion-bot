import os
import requests
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
    # ユーザーのメッセージを取得（メンション部分 <@U...> を削除）
    text = event["text"]
    user_id = event["user"]
    
    # 処理中であることを伝える（オプション）
    # say(f"考え中...") 

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
        
        # Difyからの返事を取り出す
        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "（答えが見つかりませんでした）")
            say(answer)
        else:
            say(f"エラーが発生しました: {response.text}")
            
    except Exception as e:
        say(f"システムエラー: {str(e)}")

# ボットを起動
if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
