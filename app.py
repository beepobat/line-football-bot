import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# เพิ่มบรรทัดนี้: นำเข้าฟังก์ชันดึงผลบอลที่เราเพิ่งทำ
from football_api import get_live_scores 

app = Flask(__name__)

# ดึง Key จาก Environment
CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.strip() # ตัดช่องว่างหน้าหลังออก
    
    # --- โซนตั้งค่าคำตอบ ---
    
    # 1. ถ้าพิมพ์คำว่า "ผลบอล" หรือ "โปรแกรมบอล"
    if "ผลบอล" in msg or "โปรแกรมบอล" in msg:
        # เรียกใช้ฟังก์ชันจากไฟล์ football_api.py (ของจริง)
        reply_text = get_live_scores()
    
    # 2. ถ้าพิมพ์คำว่า "บอท" หรือ "น้อง"
    elif "บอท" in msg or "น้อง" in msg:
        reply_text = "ครับผม! มีอะไรให้ช่วยเรื่องบอลไหมครับ?"
        
    # 3. ถ้าพิมพ์คำอื่น (เช่น ทักทาย)
    else:
        # บอทจะไม่ตอบอะไร (หรือจะให้ตอบกวนๆ ก็แก้ตรงนี้ได้)
        return

    # ส่งข้อความกลับไปหาผู้ใช้
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run()