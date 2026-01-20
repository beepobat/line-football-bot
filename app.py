import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# นำเข้าฟังก์ชันทั้งหมด
from football_api import get_live_scores, get_last_5_matches, get_upcoming_matches, get_standings

app = Flask(__name__)

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
    
    # 1. ดูตารางคะแนน (เช่น "ตาราง พรีเมียร์")
    if len(words) >= 2 and (words[0] in ["ตาราง", "คะแนน", "อันดับ"]):
        league_name = words[1]
        reply_text = get_standings(league_name)

    # 2. ดูโปรแกรมล่วงหน้า (เช่น "โปรแกรม แมนยู")
    elif len(words) >= 2 and (words[0] in ["โปรแกรม", "นัดต่อไป", "นัดหน้า", "โปรแกรมบอล"]):
        team_name = words[1]
        reply_text = get_upcoming_matches(team_name)

    # 3. ดูผลย้อนหลังรายทีม (เช่น "ผลบอล แมนยู")
    elif len(words) >= 2 and words[0] == "ผลบอล":
        team_name = words[1]
        reply_text = get_last_5_matches(team_name)
        
    # 4. ดูผลบอลรายวัน
    elif msg in ["ผลบอล", "โปรแกรมบอล", "เช็คผลบอล"]:
        reply_text = get_live_scores(days_offset=0)
    elif "เมื่อวาน" in msg:
        reply_text = get_live_scores(days_offset=-1)
    elif "พรุ่งนี้" in msg:
        reply_text = get_live_scores(days_offset=1)

    # 5. Help
    elif "บอท" in msg:
        reply_text = (
            "⚽ คำสั่งบอทฟุตบอล ⚽\n"
            "- 'ผลบอล' : ดูวันนี้\n"
            "- 'ผลบอล แมนยู' : ดูย้อนหลัง 5 นัด\n"
            "- 'โปรแกรม แมนยู' : ดู 3 นัดหน้า\n"
            "- 'ตาราง พรีเมียร์' : ดูคะแนน"
        )
    else:
        return

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run()