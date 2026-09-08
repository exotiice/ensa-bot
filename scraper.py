import os
import time
import threading
import requests
from bs4 import BeautifulSoup
import telebot
from http.server import HTTPServer, BaseHTTPRequestHandler

# 🌐 سيرفر وهمي صغير باش Render يقبل الخيار المجاني Web Service
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

# تشغيل السيرفر الوهمي فـ خلفية البرنامج
threading.Thread(target=run_dummy_server, daemon=True).start()

# ================= المعطيات ديالك =================
BOT_TOKEN = "8706374561:AAGqOC8BjmWrPLKCnWB6PRxf0x3f_S9w62k" 
CHAT_ID = "6631644936"

SITES = [
    {
        "name": "ENSA (Tawjihi)",
        "url": "https://www.tawjihi.ma",
        "keywords": ["نتائج", "résultats", "ensa", "لوائح", "sélection"]
    },
    {
        "name": "ENIAD",
        "url": "https://eniad.uiz.ac.ma",
        "keywords": ["eniad", "نتائج", "résultats", "لوائح", "sélection", "liste", "concours"]
    }
]

bot = telebot.TeleBot(BOT_TOKEN)

def check_site(site_info):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        response = requests.get(site_info["url"], headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().lower()

        for keyword in site_info["keywords"]:
            if keyword.lower() in page_text:
                return True, keyword, None
        return False, None, None
    except Exception as e:
        return None, None, str(e)

@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    if str(message.chat.id) == CHAT_ID:
        bot.reply_to(message, "⏳ بلاتي ندخل للموقعين بجوج (ENSA و ENIAD) ونفحصهم ليك فـ الحين...")
        report = "📊 **تقرير الفحص المباشر:**\n\n"
        for site in SITES:
            found, keyword, err = check_site(site)
            if found is True:
                report += f"🚨 **{site['name']}**: خرجت النتائج! (لقينا كلمة '{keyword}')\n🔗 {site['url']}\n\n"
            elif found is False:
                report += f"✅ **{site['name']}**: مازال ما كاين والو جديد.\n\n"
            else:
                report += f"⚠️ **{site['name']}**: مشكل فـ الاتصال ({err})\n\n"
        bot.send_message(CHAT_ID, report)

def auto_checker():
    alerted = {site["name"]: False for site in SITES}
    while True:
        time.sleep(300)
        for site in SITES:
            if not alerted[site["name"]]:
                found, keyword, _ = check_site(site)
                if found is True:
                    bot.send_message(
                        CHAT_ID, 
                        f"🚨 **تنبيه تلقائي!**\n\nخرجت النتائج فـ **{site['name']}**!\nلقينا كلمة '{keyword}' فـ الموقع:\n🔗 {site['url']}"
                    )
                    alerted[site["name"]] = True

if __name__ == "__main__":
    t = threading.Thread(target=auto_checker)
    t.daemon = True
    t.start()

    bot.send_message(CHAT_ID, "🚀 **البوت دابا كيعس على نتائج ENSA و ENIAD فـ دقة واحدة!**\n\nتقدر تصيفط ليه أي ميساج باش يدير ليك فحص مباشر لهوم بجوج.")
    bot.infinity_polling()
