import time
import threading
import requests
from bs4 import BeautifulSoup
import telebot

# ================= المعطيات ديالك =================
BOT_TOKEN = "8706374561:AAGqOC8BjmWrPLKCnWB6PRxf0x3f_S9w62k" 
CHAT_ID = "6631644936"

# 🔗 قائمة المواقع اللي غيعس عليها البوت
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
# ========================================================

bot = telebot.TeleBot(BOT_TOKEN)

def check_site(site_info):
    """فحص موقع واحد"""
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

# 📩 الفحص المباشر عند إرسال أي رسالة
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

# 🔄 الفحص التلقائي فـ الخلفية كل 5 دقائق للموقعين
def auto_checker():
    # لتفادي تكرار التنبيه التلقائي لنفس الموقع إذا خرجت نتائجه
    alerted = {site["name"]: False for site in SITES}
    
    while True:
        time.sleep(300)  # فحص كل 5 دقائق
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
    # تشغيل الفحص التلقائي فـ الخلفية
    t = threading.Thread(target=auto_checker)
    t.daemon = True
    t.start()

    # رسالة الترحيب
    bot.send_message(CHAT_ID, "🚀 **البوت دابا كيعس على نتائج ENSA و ENIAD فـ دقة واحدة!**\n\nتقدر تصيفط ليه أي ميساج باش يدير ليك فحص مباشر لهوم بجوج.")
    bot.infinity_polling()
