import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# ดึงค่ารหัสลับมาจาก Server (เดี๋ยวเราไปตั้งค่าใน Render อีกที)
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/", methods=['GET'])
def home():
    return "Football Bot is Running!", 200

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.strip()
    
    # --- โซนตั้งเงื่อนไขการตอบ ---
    
    # 1. ถ้าพิมพ์คำว่า "ผลบอล" หรือ "สถิติ"
    if "ผลบอล" in msg or "สถิติ" in msg:
        reply_text = f"ได้รับคำสั่งหาข้อมูล: {msg} \n(เดี๋ยวผมไปดึงข้อมูลมาให้นะครับ - รอใส่โค้ดจริง)"
    
    # 2. ถ้าเรียก "บอท" หรือ "น้อง"
    elif "บอท" in msg or "น้อง" in msg:
        reply_text = "ครับผม! มีอะไรให้ช่วยเรื่องบอลไหมครับ?"
        
    # 3. ถ้าคุยเรื่องอื่นในกลุ่ม ให้เงียบไว้ (จะได้ไม่รบกวน)
    else:
        return

    # ส่งข้อความกลับ
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run()