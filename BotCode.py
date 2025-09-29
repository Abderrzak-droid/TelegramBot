import requests
import time
import html
import feedparser
from bs4 import BeautifulSoup
from telegram import Bot
from flask import Flask, render_template_string
import threading

# Your bot token
TOKEN = "7607971085:AAHAnStvvonu63K1vSD8UTQK8VEQpXG1hiE"
bot = Bot(token=TOKEN)

# Your Telegram user ID (replace with your real ID)
YOUR_TELEGRAM_ID = 5963925921  # <-- Replace this later

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
    # You can serve the HTML version or just return this for now
    return render_template_string('''
   import React, { useState, useEffect } from 'react';
import { Activity, Radio, Newspaper, Globe, CheckCircle, Clock, TrendingUp } from 'lucide-react';

export default function BotStatusPage() {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [pulseActive, setPulseActive] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    const pulse = setInterval(() => setPulseActive(prev => !prev), 2000);
    return () => {
      clearInterval(timer);
      clearInterval(pulse);
    };
  }, []);

  const stats = [
    { icon: Radio, label: 'Status', value: 'Online', color: 'text-green-400' },
    { icon: Newspaper, label: 'Sources', value: '5 Feeds', color: 'text-blue-400' },
    { icon: Clock, label: 'Check Interval', value: '5 min', color: 'text-purple-400' },
    { icon: TrendingUp, label: 'Uptime', value: '99.9%', color: 'text-yellow-400' }
  ];

  const keywords = ['الجزائر', 'الجيش', 'المخابرات', 'المغرب', 'التجسس', 'المؤسسة العسكرية'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse delay-1000"></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-12 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-400 to-blue-500 rounded-2xl mb-6 shadow-2xl transform hover:scale-110 transition-transform duration-300">
            <Activity className="w-10 h-10 text-white" strokeWidth={2.5} />
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-green-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
            Arabic News Monitor
          </h1>
          <p className="text-xl text-gray-300 mb-2">Telegram Bot Service</p>
          <div className="flex items-center justify-center gap-2 text-sm text-gray-400">
            <Globe className="w-4 h-4" />
            <span>{currentTime.toLocaleString('ar-DZ', { timeZone: 'Africa/Algiers' })}</span>
          </div>
        </div>

        {/* Status Card */}
        <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 mb-8 border border-white/20 shadow-2xl">
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className={`relative ${pulseActive ? 'scale-110' : 'scale-100'} transition-transform duration-500`}>
              <div className="absolute inset-0 bg-green-400 rounded-full blur-xl opacity-50"></div>
              <CheckCircle className="relative w-16 h-16 text-green-400" strokeWidth={2} />
            </div>
            <div>
              <h2 className="text-4xl font-bold text-green-400">Bot is Active</h2>
              <p className="text-gray-300">All systems operational</p>
            </div>
          </div>
          
          <div className="h-2 bg-gradient-to-r from-green-400 via-blue-400 to-purple-400 rounded-full animate-pulse"></div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, idx) => (
            <div key={idx} className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300 transform hover:-translate-y-1">
              <stat.icon className={`w-8 h-8 ${stat.color} mb-3`} />
              <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
              <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
            </div>
          ))}
        </div>

        {/* Keywords Section */}
        <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-2xl mb-8">
          <h3 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Newspaper className="w-6 h-6 text-blue-400" />
            Monitored Keywords
          </h3>
          <div className="flex flex-wrap gap-3">
            {keywords.map((keyword, idx) => (
              <span
                key={idx}
                className="px-4 py-2 bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-full border border-purple-400/30 text-purple-200 font-medium hover:from-purple-500/30 hover:to-blue-500/30 transition-all duration-300"
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>

        {/* News Sources */}
        <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-2xl">
          <h3 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Radio className="w-6 h-6 text-green-400" />
            Active News Sources
          </h3>
          <div className="space-y-3">
            {['الشروق (Echorouk)', 'البلاد (El Bilad)', 'النهار (Ennahar)', 'TSA Algérie', 'هسبريس (Hespress)'].map((source, idx) => (
              <div key={idx} className="flex items-center gap-3 p-3 bg-white/5 rounded-xl hover:bg-white/10 transition-all duration-300">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-gray-200">{source}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-400 text-sm">
          <p>Powered by Telegram Bot API • Monitoring Arabic News 24/7</p>
        </div>
      </div>
    </div>
  );
}
    ''')

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