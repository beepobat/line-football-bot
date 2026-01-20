import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# นำเข้าฟังก์ชันจาก football_api.py (ต้องชื่อไฟล์ตรงกันนะ)
from football_api import get_live_scores, get_last_5_matches, get_upcoming_matches

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
    msg = event.message.text.strip()
    words = msg.split()
    
    # 1. เช็คโปรแกรมล่วงหน้า (เช่น "โปรแกรม แมนยู", "นัดหน้า ลิเวอร์พูล")
    if len(words) >= 2 and (words[0] in ["โปรแกรม", "นัดต่อไป", "นัดหน้า", "โปรแกรมบอล"]):
        team_name = words[1]
        reply_text = get_upcoming_matches(team_name)

    # 2. เช็คผลย้อนหลังรายทีม (เช่น "ผลบอล แมนยู")
    elif len(words) >= 2 and words[0] == "ผลบอล":
        team_name = words[1]
        reply_text = get_last_5_matches(team_name)
        
    # 3. เช็คผลบอลรายวัน (ระบุวัน)
    elif "ผลบอลเมื่อวาน" in msg:
        reply_text = get_live_scores(days_offset=-1)
    elif "พรุ่งนี้" in msg: # เผื่อพิมพ์ว่า "โปรแกรมบอลพรุ่งนี้"
        reply_text = get_live_scores(days_offset=1)

    # 4. เช็คผลบอลวันนี้ (คำสั่งปกติ)
    elif msg in ["ผลบอล", "โปรแกรมบอล", "เช็คผลบอล", "ผลบอลวันนี้"]:
        reply_text = get_live_scores(days_offset=0)
        
    # 5. คุยเล่น / ถามวิธีใช้
    elif "บอท" in msg or "น้อง" in msg:
        reply_text = (
            "⚽ สั่งผมได้เลยครับ:\n"
            "- พิมพ์ 'ผลบอล' : ดูคู่ที่เตะวันนี้\n"
            "- พิมพ์ 'ผลบอลเมื่อวาน' : ดูย้อนหลัง\n"
            "- พิมพ์ 'ผลบอล แมนยู' : ดูผล 5 นัดหลังสุด\n"
            "- พิมพ์ 'โปรแกรม แมนยู' : ดู 3 นัดถัดไป"
        )
    else:
        # ถ้าพิมพ์อย่างอื่นมา บอทจะไม่ตอบ (ป้องกันการรบกวนในกลุ่ม)
        return

    # ส่งข้อความกลับ
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run()