import os
import google.generativeai as genai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# นำเข้าฟังก์ชันฟุตบอล
from football_api import get_live_scores, get_last_5_matches, get_upcoming_matches, get_standings

app = Flask(__name__)

# --- ตั้งค่า LINE ---
CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# --- ตั้งค่า AI ---
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

# ใช้โมเดลที่คุณเลือก (ถ้า 2.5 ใช้ได้ก็จัดไปครับ หรือจะใช้ 1.5-flash ก็ได้)
# ในโค้ดนี้ผมใส่เป็นตัวแปรไว้ให้ ถ้าอยากเปลี่ยนรุ่นก็แก้ตรง string นี้ได้เลย
model = genai.GenerativeModel('models/gemini-2.5-flash') 

def ask_gemini(user_text):
    try:
        # --- ปรับจูน Prompt ใหม่ตรงนี้ครับ ---
        system_prompt = """
        คุณคือ 'จารย์เซียน' กูรูฟุตบอลปากจัด แฟนบอลตัวยงที่วิเคราะห์เกมขาดเหมือนโค้ชมาเอง
        
        บุคลิกของคุณ:
        - ปากแซ่บ กวนตีน ขี้ขิง: ใช้ศัพท์บอลไทยสไตล์โซเชียล (เช่น คาบ้าน, รูรั่ว, สากกะเบือ, รถผ้าป่าคว่ำ, กรรมการกาว)
        - ไม่ต้องสุภาพมาก: คุยเหมือนเพื่อนสนิทในวงเหล้า (แต่ไม่หยาบคายจนโดนแบน) ให้ฟีลเป็นกันเอง
        - มั่นใจในข้อมูล: วิเคราะห์ฟอร์มการเล่น แทคติกโค้ช การจัดตัวผู้เล่น (วิจารณ์ได้เต็มที่ว่าใครเล่นห่วย ใครแบกทีม)
        
        แนวทางการตอบ:
        - ถ้าถามเรื่องบอล: วิเคราะห์เจาะลึก อย่าตอบกว้างๆ เช่น ถ้าถามเรื่องแมนยู ให้วิเคราะห์ถึงแผนการเล่น หรือด่านักเตะที่ฟอร์มตก
        - ถ้าถามเรื่องอื่น: คุยได้ปกติ แต่พยายามวกเข้าเรื่องบอล หรือเปรียบเทียบกับฟุตบอลแบบฮาๆ
        - ข้อควรระวัง: ถ้าเป็นผลบอลสดหรือโปรแกรมแข่งที่ยังไม่เกิดขึ้นและคุณไม่รู้ข้อมูลแน่ชัด ให้ไล่ user ไปใช้คำสั่ง "ผลบอล [ชื่อทีม]" หรือ "โปรแกรม [ชื่อทีม]" แทน อย่ามั่วสกอร์

        บริบท: ตอนนี้คุณคุยอยู่ใน LINE Group กับแก๊งเพื่อนดูบอล
        """
        
        # รวมคำสั่ง Prompt เข้ากับข้อความของ User
        response = model.generate_content(f"{system_prompt}\n\nUser ถามว่า: {user_text}")
        return response.text.strip()
        
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "โทษที ไวไฟที่ร้านเหล้าไม่ค่อยดี สมองเบลอชั่วคราว (AI Error)"

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
    msg_lower = msg.lower() # แปลงเป็นตัวเล็กเพื่อเช็คคำง่ายๆ
    
    reply_text = ""

    # --- โซน 1: คำสั่งฟุตบอล (ทำงานทันที ไม่ต้องเรียกชื่อ) ---
    if len(words) >= 2 and (words[0] in ["ตาราง", "คะแนน", "อันดับ"]):
        reply_text = get_standings(words[1])
    elif len(words) >= 2 and (words[0] in ["โปรแกรม", "นัดต่อไป", "นัดหน้า", "โปรแกรมบอล"]):
        reply_text = get_upcoming_matches(words[1])
    elif len(words) >= 2 and words[0] == "ผลบอล":
        reply_text = get_last_5_matches(words[1])
    elif msg in ["ผลบอล", "โปรแกรมบอล", "เช็คผลบอล", "สกอร์", "score"]:
        reply_text = get_live_scores(days_offset=0)
    elif "เมื่อวาน" in msg:
        reply_text = get_live_scores(days_offset=-1)
    elif "พรุ่งนี้" in msg:
        reply_text = get_live_scores(days_offset=1)
    
    # --- โซน 2: คุยกับ AI (ต้องเรียกชื่อก่อนถึงจะตอบ) ---
    # เช็คว่ามีคำว่า บอท, น้อง, bot หรือ @ อยู่ในประโยคไหม
    elif "บอท" in msg or "น้อง" in msg or "bot" in msg_lower or "@" in msg:
        # ส่งข้อความไปให้ AI ตอบ
        reply_text = ask_gemini(msg)

    # --- โซน 3: ถ้าไม่เข้าเงื่อนไขอะไรเลย ---
    else:
        # เงียบ (Return ออกไปเลย ไม่ส่งอะไรกลับ)
        return

    # ส่งคำตอบกลับ LINE (เฉพาะถ้ามี reply_text)
    if reply_text:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

if __name__ == "__main__":
    app.run()