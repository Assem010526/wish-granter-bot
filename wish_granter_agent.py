#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wish Granter — Instagram Analytics Agent для Balazone
Webhook версия для Render.com (бесплатный хостинг)
"""

import requests
import os
from datetime import datetime
from flask import Flask, request, jsonify

# ===== НАСТРОЙКИ =====
INSTAGRAM_TOKEN = "EAAVBWGTyJv4BRqZCeW3OFGRkiwmQ9Di4jZCb0BLo99kd9gQtRZC3lM0ZAEOYklFDNRDWtxsQ1r2vIE8ShXZCZBYplSoY5aaOKgK5ZCfDs1fAA2VS5wTONdQ7PgZCSNB5yZB6FtyDGNKEbmssh2caAmTkUQjWjwZAIHxIofCVg4ZBsaOLNFwnxHLZCiSK3tSyIrbFyz7K8QZDZD"
INSTAGRAM_ACCOUNT_ID = "17841465631046584"
TELEGRAM_TOKEN = "8259042725:AAHWIwIOTo4-zCtBL0klgUZ3-O7K0YqYhwc"
CHAT_ID = 446497122  # Асем Арып — Telegram Chat ID

app = Flask(__name__)

# ===== TELEGRAM =====

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=data, timeout=10)
        return r.ok
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False

# ===== INSTAGRAM =====

def get_recent_posts():
    url = f"https://graph.facebook.com/v20.0/{INSTAGRAM_ACCOUNT_ID}/media"
    params = {
        "access_token": INSTAGRAM_TOKEN,
        "fields": "id,caption,media_type,timestamp,like_count,comments_count",
        "limit": 12
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.json().get("data", [])
    except Exception as e:
        print(f"Ошибка Instagram API: {e}")
        return []

def get_account_info():
    url = f"https://graph.facebook.com/v20.0/{INSTAGRAM_ACCOUNT_ID}"
    params = {
        "access_token": INSTAGRAM_TOKEN,
        "fields": "followers_count,media_count,name"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if "error" in data:
            send_telegram(f"🔴 Instagram API ошибка:\n{data['error'].get('message', str(data['error']))}")
        return data
    except Exception as e:
        send_telegram(f"🔴 Instagram запрос упал: {e}")
        return {}

# ===== ОТЧЁТ =====

CONTENT_IDEAS = [
    "🎬 Видео: покажи как аппарат готовит смесь за 30 секунд",
    "👶 Фото: счастливый малыш рядом с аппаратом Balazone",
    "📦 Распаковка: покажи комплектацию аппарата",
    "💬 Отзыв: поделись реальным отзывом покупателя",
    "🔄 Сравнение: Balazone vs приготовление вручную",
    "❓ Вопрос-ответ: ответь на частый вопрос о продукте",
    "🎯 Факт: расскажи интересный факт о детском питании",
    "🛒 Акция: напомни о покупке через Kaspi",
]

def make_report():
    now = datetime.now()
    idea = CONTENT_IDEAS[now.weekday() % len(CONTENT_IDEAS)]

    posts = get_recent_posts()
    account = get_account_info()

    followers = account.get("followers_count", "—")
    media_count = account.get("media_count", "—")

    if posts:
        avg_likes = sum(p.get("like_count", 0) for p in posts) / len(posts)
        avg_comments = sum(p.get("comments_count", 0) for p in posts) / len(posts)
        best = max(posts, key=lambda x: x.get("like_count", 0) + x.get("comments_count", 0) * 3)
        best_type = best.get("media_type", "IMAGE")
        type_ru = {"IMAGE": "📷 Фото", "VIDEO": "🎬 Видео", "CAROUSEL_ALBUM": "🖼 Карусель"}.get(best_type, best_type)
        best_date = best.get("timestamp", "")[:10]
        best_caption = (best.get("caption", "") or "")[:60]

        stats_text = f"""📈 <b>Статистика аккаунта:</b>
• Подписчиков: {followers}
• Всего постов: {media_count}
• Среднее лайков: {avg_likes:.0f}
• Среднее комментариев: {avg_comments:.1f}

🏆 <b>Лучший пост за последнее время:</b>
• Тип: {type_ru}
• Лайков: {best.get('like_count', 0)} | Комментариев: {best.get('comments_count', 0)}
• Дата: {best_date}
• Текст: {best_caption}..."""
    else:
        stats_text = f"📈 Подписчиков: {followers} | Постов: {media_count}"

    return f"""🤖 <b>Wish Granter — Ежедневный отчёт</b>
📅 {now.strftime('%d.%m.%Y, %H:%M')}

{stats_text}

💡 <b>Идея контента на сегодня:</b>
{idea}

⏰ <b>Лучшее время для публикации:</b>
12:00–13:00 или 19:00–21:00

#balazone #babybrezza #детскаясмесь #кормлениемладенца"""

# ===== FLASK ENDPOINTS =====

@app.route("/", methods=["GET"])
def home():
    return "Wish Granter Bot is running! 🤖"

@app.route(f"/webhook", methods=["POST"])
def webhook():
    """Telegram отправляет сюда все сообщения"""
    data = request.get_json()
    if data and "message" in data:
        text = data["message"].get("text", "").lower()
        chat_id_incoming = data["message"]["chat"]["id"]
        if chat_id_incoming == CHAT_ID:
            if "debug" in text:
                import requests as req
                r1 = req.get(f"https://graph.facebook.com/v20.0/{INSTAGRAM_ACCOUNT_ID}",
                    params={"access_token": INSTAGRAM_TOKEN, "fields": "followers_count,media_count,name"}, timeout=10)
                send_telegram(f"Account API:\n{r1.text[:1000]}")
                r2 = req.get(f"https://graph.facebook.com/v20.0/{INSTAGRAM_ACCOUNT_ID}/media",
                    params={"access_token": INSTAGRAM_TOKEN, "fields": "id,like_count", "limit": 3}, timeout=10)
                send_telegram(f"Media API:\n{r2.text[:1000]}")
            elif "отчет" in text or "отчёт" in text or "/report" in text or "/start" in text:
                report = make_report()
                send_telegram(report)
    return jsonify({"ok": True})

@app.route("/trigger_report", methods=["GET", "POST"])
def trigger_report():
    """Cron-job.org вызывает этот URL каждый день в 08:00"""
    report = make_report()
    success = send_telegram(report)
    return jsonify({"ok": success, "time": datetime.now().isoformat()})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🤖 Wish Granter запускается на порту {port}...")
    app.run(host="0.0.0.0", port=port)
