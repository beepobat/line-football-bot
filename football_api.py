import os
import requests
import json
from datetime import datetime, timedelta

# ดึง Key จาก Environment
API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY')

# --- 1. สมุดจดชื่อลีก (สำหรับเรียกดูตารางคะแนน) ---
LEAGUE_MAPPING = {
    'พรีเมียร์': 'PL', 'พรีเมียร์ลีก': 'PL', 'อังกฤษ': 'PL', 'pl': 'PL',
    'ลาลีกา': 'PD', 'สเปน': 'PD', 'pd': 'PD',
    'บุนเดส': 'BL1', 'บุนเดสลีกา': 'BL1', 'เยอรมัน': 'BL1', 'bl1': 'BL1',
    'กัลโช่': 'SA', 'เซเรียอา': 'SA', 'อิตาลี': 'SA', 'sa': 'SA',
    'ลีกเอิง': 'FL1', 'ฝรั่งเศส': 'FL1', 'fl1': 'FL1'
}

# --- 2. สมุดจดชื่อเล่นทีม (ฉบับสมบูรณ์ ครบ 5 ลีก + ทีมเล็ก + ทีมเลื่อนชั้น) ---
TEAM_MAPPING = {
    # 🏴󠁧󠁢󠁥󠁮󠁧󠁿 พรีเมียร์ลีก
    'แมนยู': 66, 'ผีแดง': 66, 'manutd': 66, 'mu': 66,
    'ลิเวอร์พูล': 64, 'หงส์': 64, 'liverpool': 64, 'lfc': 64,
    'อาร์เซนอล': 57, 'ปืนใหญ่': 57, 'arsenal': 57,
    'เชลซี': 61, 'สิงห์บลู': 61, 'chelsea': 61,
    'แมนซิตี้': 65, 'เรือใบ': 65, 'mancity': 65,
    'สเปอร์ส': 73, 'ไก่เดือยทอง': 73, 'spurs': 73,
    'นิวคาสเซิล': 67, 'สาลิกา': 67, 'newcastle': 67,
    'เอฟเวอร์ตัน': 62, 'ทอฟฟี่': 62, 'everton': 62,
    'วิลล่า': 58, 'แอสตันวิลล่า': 58, 'astonvilla': 58,
    'เวสต์แฮม': 563, 'ขุนค้อน': 563, 'westham': 563,
    'เลสเตอร์': 338, 'จิ้งจอก': 338, 'leicester': 338,
    'ไบรท์ตัน': 397, 'brighton': 397,
    'วูล์ฟ': 76, 'wolves': 76,
    'พาเลซ': 354, 'คริสตัลพาเลซ': 354, 'crystalpalace': 354,
    'เบรนท์ฟอร์ด': 402, 'brentford': 402,
    'ฟูแล่ม': 63, 'fulham': 63,
    'ฟอเรสต์': 351, 'forest': 351,
    'บอร์นมัธ': 1044, 'bournemouth': 1044,
    'เซาแธมป์ตัน': 340, 'southampton': 340,
    'อิปสวิช': 349, 'ipswich': 349,

    # 🇪🇸 ลาลีกา
    'มาดริด': 86, 'เรอัลมาดริด': 86, 'realmadrid': 86,
    'บาร์ซ่า': 81, 'บาร์เซโลน่า': 81, 'barcelona': 81,
    'แอตมาดริด': 78, 'atletico': 78,
    'เซบีย่า': 559, 'sevilla': 559,
    'บาเลนเซีย': 95, 'valencia': 95,
    'บียาร์เรอัล': 94, 'villarreal': 94,
    'โซเซียดาด': 92, 'sociedad': 92,
    'บิลเบา': 77, 'athletic': 77, 'athleticclub': 77,
    'เอสปันญ่อล': 80, 'espanyol': 80,
    'เลกาเนส': 745, 'leganes': 745,
    'บายาโดลิด': 250, 'valladolid': 250,
    'เบติส': 90, 'betis': 90,
    'จิโรน่า': 298, 'girona': 298,
    'เซลต้า': 558, 'celta': 558,
    'มายอร์ก้า': 89, 'mallorca': 89,
    'ราโย': 87, 'rayo': 87,
    'โอซาซูน่า': 79, 'osasuna': 79,
    'เกตาเฟ่': 82, 'getafe': 82,
    'ลาสปัลมาส': 275, 'laspalmas': 275,
    'อลาเบส': 263, 'alaves': 263,

    # 🇩🇪 บุนเดสลีกา
    'บาเยิร์น': 5, 'เสือใต้': 5, 'bayern': 5,
    'ดอร์ทมุนด์': 4, 'เสือเหลือง': 4, 'dortmund': 4,
    'เลเวอร์คูเซ่น': 3, 'ห้างยา': 3, 'leverkusen': 3,
    'ไลป์ซิก': 721, 'leipzig': 721,
    'แฟรงก์เฟิร์ต': 19, 'frankfurt': 19,
    'โวล์ฟสบวร์ก': 11, 'wolfsburg': 11,
    'กลัดบัค': 18, 'gladbach': 18,
    'ออกสบวร์ก': 16, 'augsburg': 16,
    'ซังต์เพาลี': 35, 'stpauli': 35,
    'โฮลสไตน์คีล': 720, 'holsteinkiel': 720, 'kiel': 720,
    'สตุ๊ตการ์ท': 10, 'stuttgart': 10,
    'ไฟร์บวร์ก': 17, 'freiburg': 17,
    'ฮอฟเฟนไฮม์': 2, 'hoffenheim': 2,
    'ไมนซ์': 15, 'mainz': 15,
    'ยูเนี่ยนเบอร์ลิน': 28, 'unionberlin': 28,
    'เบรเมน': 12, 'werder': 12,
    'โบคุ่ม': 36, 'bochum': 36,
    'ไฮเดนไฮม์': 44, 'heidenheim': 44,

    # 🇮🇹 กัลโช่ เซเรียอา
    'ยูเวนตุส': 109, 'juve': 109,
    'มิลาน': 98, 'milan': 98,
    'อินเตอร์': 108, 'inter': 108,
    'โรม่า': 100, 'roma': 100,
    'นาโปลี': 113, 'napoli': 113,
    'ลาซิโอ': 110, 'lazio': 110,
    'ฟิออ': 99, 'fiorentina': 99,
    'อตาลันต้า': 102, 'atalanta': 102,
    'โคโม': 1047, 'como': 1047,
    'กายารี่': 104, 'cagliari': 104,
    'ปาร์ม่า': 112, 'parma': 112,
    'เอ็มโปลี': 445, 'empoli': 445,
    'เวเนเซีย': 454, 'venezia': 454,
    'โบโลญญ่า': 103, 'bologna': 103,
    'โตริโน่': 586, 'torino': 586,
    'อูดิเนเซ่': 115, 'udinese': 115,
    'เจนัว': 107, 'genoa': 107,
    'มอนซ่า': 5911, 'monza': 5911,
    'เลชเช่': 5890, 'lecce': 5890,
    'เวโรน่า': 450, 'verona': 450,

    # 🇫🇷 ลีกเอิง
    'ปารีส': 524, 'psg': 524,
    'มาร์กเซย': 523, 'marseille': 523,
    'ลียง': 529, 'lyon': 529,
    'โมนาโก': 548, 'monaco': 548,
    'ลีลล์': 521, 'lille': 521,
    'ตูลูส': 511, 'toulouse': 511,
    'แบรสต์': 512, 'brest': 512,
    'อองเซ่ร์': 532, 'angers': 532,
    'ลอริยองต์': 525, 'lorient': 525,
    'เลออาฟ': 538, 'lehavre': 538,
    'โอแชร์': 519, 'auxerre': 519,
    'เม็ตซ์': 545, 'metz': 545,
    'ล็องส์': 546, 'lens': 546,
    'แรนส์': 550, 'rennes': 550,
    'นีซ': 522, 'nice': 522,
    'สตราสบูร์ก': 576, 'strasbourg': 576,
    'แร็งส์': 511, 'reims': 511,
    'น็องต์': 543, 'nantes': 543,
    'มงต์เปลลิเย่ร์': 518, 'montpellier': 518,
    'แซงต์เอเตียน': 527, 'saintetienne': 527
}

# --- Helper: แปลงเวลา UTC เป็นเวลาไทย ---
def convert_to_thai_time(utc_date_str):
    try:
        utc_dt = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%SZ")
        thai_dt = utc_dt + timedelta(hours=7)
        return thai_dt
    except:
        return datetime.now()

# --- ฟังก์ชัน 1: ดูผลบอลรายวัน (เวลาไทย) ---
def get_live_scores(days_offset=0):
    url = "https://api.football-data.org/v4/matches"
    headers = {'X-Auth-Token': API_KEY}
    
    target_date = datetime.now() + timedelta(days=days_offset)
    date_str = target_date.strftime('%Y-%m-%d')
    
    params = {
        'status': 'FINISHED,LIVE,PAUSED,SCHEDULED',
        'dateFrom': date_str,
        'dateTo': date_str
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            
            if not matches:
                return f"วันที่ {date_str} ไม่มีรายการแข่งในลีกหลักๆ ครับ"
            
            if days_offset == 0: title = "⚽ โปรแกรม/ผลบอล **วันนี้** ⚽"
            elif days_offset == -1: title = f"⚽ ผลบอล **เมื่อวาน** ({date_str}) ⚽"
            elif days_offset == 1: title = f"⚽ โปรแกรมบอล **พรุ่งนี้** ({date_str}) ⚽"
            else: title = f"⚽ ผลบอลวันที่ {date_str} ⚽"

            reply_msg = f"{title}\n(เวลาไทย 🇹🇭)\n\n"
            
            # รวมรหัสลีกและถ้วยทั้งหมดที่น่าสนใจ
            target_leagues = [
                'PL', 'PD', 'CL', 'BL1', 'SA', 'FL1', # ลีกหลัก
                'FAC', 'FLC', 'CDR', 'DFB', 'CIT', 'CDF', # บอลถ้วยในประเทศ
                'EL', 'CLI', 'WC', 'EC' # บอลถ้วยยุโรป/ทีมชาติ
            ]
            
            found_match = False
            for match in matches:
                league_code = match['competition']['code']
                
                # เช็คว่าอยู่ในลีก/ถ้วยที่เราสนใจไหม
                if league_code in target_leagues:
                    found_match = True
                    thai_time = convert_to_thai_time(match['utcDate'])
                    time_str = thai_time.strftime('%H:%M')
                    
                    home = match['homeTeam']['shortName']
                    away = match['awayTeam']['shortName']
                    status = match['status']
                    
                    # ชื่อรายการแข่ง (เช่น UCL, FA Cup) - ใส่ให้รู้ว่าเป็นถ้วยอะไร
                    comp_name = match['competition']['name']
                    # ย่อชื่อถ้วยให้สั้นลงหน่อยจะได้ไม่รก
                    comp_name = comp_name.replace("Premier League", "").replace("UEFA Champions League", "UCL").replace("FA Cup", "FA Cup") 
                    
                    if comp_name.strip(): comp_str = f" ({comp_name.strip()})"
                    else: comp_str = ""

                    if status in ['FINISHED', 'LIVE', 'PAUSED']:
                        score_home = match['score']['fullTime']['home']
                        score_away = match['score']['fullTime']['away']
                        if score_home is None: score_home = 0
                        if score_away is None: score_away = 0
                        reply_msg += f"⏰ {time_str} : {home} {score_home}-{score_away} {away} {status}{comp_str}\n"
                    else:
                        reply_msg += f"⏰ {time_str} : {home} vs {away}{comp_str}\n"
            
            if not found_match: return f"วันที่ {date_str} มีเตะครับ แต่เป็นลีกรองที่ไม่ได้ดึงมาโชว์"
            return reply_msg
        else:
            return f"เชื่อมต่อ API ไม่ได้ (Code: {response.status_code})"
    except Exception as e:
        return f"เกิดข้อผิดพลาด: {e}"

# --- ฟังก์ชัน 2: ดูผลย้อนหลัง 5 นัด ---
def get_last_5_matches(team_name):
    team_id = TEAM_MAPPING.get(team_name.lower())
    if not team_id: return f"ไม่พบทีม '{team_name}' ในระบบครับ"

    url = f"https://api.football-data.org/v4/teams/{team_id}/matches"
    headers = {'X-Auth-Token': API_KEY}
    params = {'status': 'FINISHED', 'limit': 50}

    try:
        response = requests.get(url, headers=headers, params=params)
        matches = response.json().get('matches', [])
        if not matches: return "ไม่พบข้อมูลย้อนหลังครับ"
        
        last_5 = matches[::-1][:5]
        reply_msg = f"📊 **ผล 5 นัดหลังสุด: {team_name}** 📊\n\n"
        
        for match in last_5:
            thai_time = convert_to_thai_time(match['utcDate'])
            date_str = thai_time.strftime('%d/%m')
            
            home = match['homeTeam']['shortName']
            away = match['awayTeam']['shortName']
            score_h = match['score']['fullTime']['home']
            score_a = match['score']['fullTime']['away']
            
            is_home = (match['homeTeam']['id'] == team_id)
            my_score = score_h if is_home else score_a
            opp_score = score_a if is_home else score_h
            
            if my_score > opp_score: icon = "✅"
            elif my_score < opp_score: icon = "❌"
            else: icon = "➖"
            
            reply_msg += f"{icon} {date_str}: {home} {score_h}-{score_a} {away}\n"
        return reply_msg
    except Exception as e: return f"Error: {e}"

# --- ฟังก์ชัน 3: ดูโปรแกรมล่วงหน้า 3 นัด (เวลาไทย) ---
def get_upcoming_matches(team_name):
    team_id = TEAM_MAPPING.get(team_name.lower())
    if not team_id: return f"ไม่พบทีม '{team_name}' ในระบบครับ"

    url = f"https://api.football-data.org/v4/teams/{team_id}/matches"
    headers = {'X-Auth-Token': API_KEY}
    params = {'status': 'SCHEDULED', 'limit': 10}

    try:
        response = requests.get(url, headers=headers, params=params)
        matches = response.json().get('matches', [])
        if not matches: return "ยังไม่มีโปรแกรมแข่งเร็วๆ นี้ครับ"
        
        next_3 = matches[:3]
        reply_msg = f"📅 **โปรแกรม 3 นัดถัดไป: {team_name}** 📅\n(เวลาไทย 🇹🇭)\n\n"
        
        for match in next_3:
            thai_time = convert_to_thai_time(match['utcDate'])
            date_str = thai_time.strftime('%d/%m')
            time_str = thai_time.strftime('%H:%M')
            
            home = match['homeTeam']['shortName']
            away = match['awayTeam']['shortName']
            competition = match['competition']['name']
            
            reply_msg += f"🗓 {date_str} {time_str}\n⚽ {home} vs {away}\n🏆 {competition}\n\n"
            
        return reply_msg
    except Exception as e: return f"Error: {e}"

# --- ฟังก์ชัน 4: ดูตารางคะแนน ---
def get_standings(league_name):
    league_code = LEAGUE_MAPPING.get(league_name)
    if not league_code:
        return "ไม่พบชื่อลีกครับ ลองพิมพ์: ตาราง พรีเมียร์, ตาราง ลาลีกา, ตาราง กัลโช่, ตาราง บุนเดส"

    url = f"https://api.football-data.org/v4/competitions/{league_code}/standings"
    headers = {'X-Auth-Token': API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        standings = data.get('standings', [])
        
        if not standings: return "ยังไม่มีข้อมูลตารางคะแนนครับ"
        
        table = standings[0]['table']
        top_10 = table[:10]
        
        reply_msg = f"🏆 **ตารางคะแนน: {league_name}** 🏆\n\n"
        reply_msg += "อันดับ | ทีม | แข่ง | แต้ม\n"
        reply_msg += "--------------------------\n"
        
        for row in top_10:
            rank = row['position']
            team = row['team']['shortName']
            played = row['playedGames']
            points = row['points']
            reply_msg += f"{rank}. {team} | {played} | {points}\n"
            
        return reply_msg
    except Exception as e: return f"Error: {e}"