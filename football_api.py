import os  
import requests
import json
from datetime import datetime

# ใส่ API Key ที่ได้จากอีเมลตรงนี้
API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY')  <-- ปิดบรรทัดนี้ไว้ก่อน

def get_live_scores():
    # URL สำหรับดูบอลที่เตะ "วันนี้"
    url = "https://api.football-data.org/v4/matches"
    
    headers = {
        'X-Auth-Token': API_KEY
    }
    
    # กรองเฉพาะคู่ที่กำลังเตะ (LIVE), พักครึ่ง (PAUSED), หรือจบแล้ว (FINISHED)
    # หรือถ้าอยากได้โปรแกรมวันนี้ทั้งหมด ตัด params ออกได้เลย
    params = {
        'status': 'LIVE,PAUSED,FINISHED,SCHEDULED',
        'dateFrom': datetime.now().strftime('%Y-%m-%d'),
        'dateTo': datetime.now().strftime('%Y-%m-%d')
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            
            if not matches:
                return "วันนี้ไม่มีรายการแข่งในลีกหลักๆ ครับ"
            
            # สร้างข้อความตอบกลับสวยๆ
            reply_msg = "⚽ **โปรแกรม/ผลบอลวันนี้** ⚽\n\n"
            
            # เลือกเฉพาะลีกดังๆ (EPL, LaLiga, UCL) เพื่อไม่ให้รก
            # PL=พรีเมียร์, PD=ลาลีกา, CL=UCL
            target_leagues = ['PL', 'PD', 'CL', 'BL1', 'SA'] 
            
            found_match = False
            for match in matches:
                league_code = match['competition']['code']
                
                # ถ้าเป็นลีกที่เราสนใจ
                if league_code in target_leagues:
                    found_match = True
                    time_str = match['utcDate'][11:16] # ตัดเอาแค่เวลา
                    home = match['homeTeam']['shortName']
                    away = match['awayTeam']['shortName']
                    
                    # เช็คสถานะสกอร์
                    status = match['status']
                    if status in ['FINISHED', 'LIVE', 'PAUSED']:
                        score_home = match['score']['fullTime']['home']
                        score_away = match['score']['fullTime']['away']
                        reply_msg += f"⏰ {time_str} : {home} {score_home}-{score_away} {away} ({status})\n"
                    else:
                        reply_msg += f"⏰ {time_str} : {home} vs {away}\n"
            
            if not found_match:
                return "มีบอลเตะครับ แต่น่าจะเป็นลีกรองๆ ที่ผมไม่ได้ดึงมาโชว์"
                
            return reply_msg
        else:
            return f"เชื่อมต่อ API ไม่ได้ (Code: {response.status_code})"
            
    except Exception as e:
        return f"เกิดข้อผิดพลาด: {e}"

# ทดสอบรันดูในเครื่องก่อน
if __name__ == "__main__":
    print(get_live_scores())