import os
import google.generativeai as genai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# นำเข้าฟังก์ชันฟุตบอลของเดิม
from football_api import get_live_scores, get_last_5_matches, get_upcoming_matches, get_standings

app = Flask(__name__)

# --- ตั้งค่า LINE ---
CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# --- ตั้งค่า AI (GEMINI) ---
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') # เดี๋ยวไปใส่ใน Render
genai.configure(api_key=GEMINI_API_KEY)

# สร้างโมเดล และกำหนดนิสัย (Persona)
model = genai.GenerativeModel('gemini-pro')

def ask_gemini(user_text):
    try:
        # กำหนดคาแรคเตอร์ให้บอท
        system_prompt = """
        คุณคือ 'เซียนบอล' เพื่อนคู่คิดเรื่องฟุตบอล
        - นิสัย: กวนนิดๆ เป็นกันเอง ขี้เล่น แต่มีความรู้แน่นปึ้ก
        - ห้ามตอบยาวเกิน 3-4 บรรทัด (เดี๋ยวคนขี้เกียจอ่าน)
        - ถ้าถามเรื่องผลบอลปัจจุบัน ให้บอกผู้ใช้ว่า "พิมพ์คำว่า 'ผลบอล' สิเดี๋ยวผมดึงให้"
        - ตอบเป็นภาษาไทยเท่านั้น
        """
        
        full_prompt = f"{system_prompt}\n\nUser: {user_text}\nAnswer:"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return "ตอนนี้สมองเบลอนิดหน่อยครับ ถามใหม่ทีนะ 😅"

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
    
    reply_text = ""

    # --- โซนคำสั่ง (Command) ---
    if len(words) >= 2 and (words[0] in ["ตาราง", "คะแนน", "อันดับ"]):
        reply_text = get_standings(words[1])
    elif len(words) >= 2 and (words[0] in ["โปรแกรม", "นัดต่อไป", "นัดหน้า"]):
        reply_text = get_upcoming_matches(words[1])
    elif len(words) >= 2 and words[0] == "ผลบอล":
        reply_text = get_last_5_matches(words[1])
    elif msg in ["ผลบอล", "โปรแกรมบอล", "เช็คผลบอล", "สกอร์"]:
        reply_text = get_live_scores(days_offset=0)
    elif "เมื่อวาน" in msg:
        reply_text = get_live_scores(days_offset=-1)
    elif "พรุ่งนี้" in msg:
        reply_text = get_live_scores(days_offset=1)
    
    # --- โซน AI (ถ้าไม่เข้าเงื่อนไขข้างบน ให้ AI ตอบ) ---
    else:
        # ส่งข้อความไปให้ Gemini ตอบ
        reply_text = ask_gemini(msg)

    # ส่งคำตอบกลับ LINE
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run()