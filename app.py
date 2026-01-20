# แก้ไขบรรทัด import ให้เรียกใช้ฟังก์ชันใหม่ด้วย
from football_api import get_live_scores, get_last_5_matches, get_upcoming_matches

# ... (ส่วนอื่นเหมือนเดิม) ...

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.strip()
    words = msg.split()
    
    # 1. ดูนัดล่วงหน้า (เช่น "โปรแกรม แมนยู", "นัดต่อไป ลิเวอร์พูล")
    if len(words) >= 2 and (words[0] in ["โปรแกรม", "นัดต่อไป", "นัดหน้า"]):
        team_name = words[1]
        reply_text = get_upcoming_matches(team_name)

    # 2. ดูผลย้อนหลัง (เช่น "ผลบอล แมนยู")
    elif len(words) >= 2 and words[0] == "ผลบอล":
        team_name = words[1]
        reply_text = get_last_5_matches(team_name)
        
    # 3. ดูผลบอลเมื่อวาน/พรุ่งนี้ (แบบระบุวัน)
    elif "ผลบอลเมื่อวาน" in msg:
        reply_text = get_live_scores(days_offset=-1)
    elif "พรุ่งนี้" in msg:
        reply_text = get_live_scores(days_offset=1)

    # 4. ดูผลบอลวันนี้ (คำสั่งปกติ)
    elif msg in ["ผลบอล", "โปรแกรมบอล", "เช็คผลบอล"]:
        reply_text = get_live_scores(days_offset=0)
        
    elif "บอท" in msg:
        reply_text = "สั่งได้เลยครับ:\n- 'ผลบอล' (ดูวันนี้)\n- 'ผลบอล แมนยู' (ดูย้อนหลัง 5 นัด)\n- 'โปรแกรม แมนยู' (ดู 3 นัดหน้า)"
    else:
        return

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )