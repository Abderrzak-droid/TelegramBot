import requests
import time
import html
import feedparser
from bs4 import BeautifulSoup
from telegram import Bot
from flask import Flask
import threading

# Your bot token
TOKEN = "7607971085:AAHAnStvvonu63K1vSD8UTQK8VEQpXG1hiE"
bot = Bot(token=TOKEN)

# Your Telegram user ID (replace with your real ID)
YOUR_TELEGRAM_ID = 123456789  # <-- Replace this later

# Arabic keywords to track
KEYWORDS = ["الجزائر", "الجيش", "المخابرات", "المغرب", "التجسس", "المؤسسة العسكرية"]

# Arabic news RSS feeds
RSS_FEEDS = [
    "https://www.echoroukonline.com/feed",
    "https://www.elbilad.net/feed",
    "https://www.ennaharonline.com/feed",
    "https://www.tsa-algerie.com/feed",
    "https://www.hespress.com/feed"
]

# Keep track of sent links
sent_links = set()

# Flask app for health checks
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running! ✅", 200

@app.route('/health')
def health():
    return "OK", 200

def get_summary(url):
    try:
        page = requests.get(url, timeout=5)
        soup = BeautifulSoup(page.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join(p.get_text() for p in paragraphs[:2])
        return html.unescape(text.strip()[:400])
    except:
        return "لا يوجد ملخص متاح حالياً."

def check_news():
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", "")
                combined = title + " " + summary

                if any(keyword in combined for keyword in KEYWORDS):
                    if link not in sent_links:
                        sent_links.add(link)
                        article_summary = get_summary(link)

                        msg = f"📰 <b>{html.escape(title)}</b>\n\n🔗 <a href='{link}'>رابط المقال</a>\n\n📝 <i>{html.escape(article_summary)}</i>"
                        try:
                            bot.send_message(chat_id=YOUR_TELEGRAM_ID, text=msg, parse_mode="HTML", disable_web_page_preview=False)
                        except Exception as e:
                            print("Failed to send:", e)
        except Exception as e:
            print(f"Error checking feed {feed_url}:", e)

def run_bot():
    while True:
        check_news()
        time.sleep(300)  # Check every 5 minutes

def run_flask():
    app.run(host='0.0.0.0', port=10000)

if __name__ == '__main__':
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Run Flask (this keeps the main thread alive)
    run_flask()