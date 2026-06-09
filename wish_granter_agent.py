#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wish Granter — Instagram Analytics Agent для Balazone
Ежедневно анализирует статистику @balazonekz и присылает рекомендации в Telegram
"""

import requests
import json
import os
import time
import sys
from datetime import datetime, timedelta

# ===== НАСТРОЙКИ =====
INSTAGRAM_TOKEN = "IGAAPBaOVtD8NBZAGJmSmFvZAXM5OTBwZAVltaVpteWlNUlpTQi0yMzBtaEY1ZAjdqRHpCYnYyLXBqX2VsMXVKc0poclN3aGhfYXlqX1R4ZA3JnY2w0UU9tZAVdmUFpZAYjBaMV9meERhWHZAyYWhic0wtSTVmSk0zT3JqcmNlckNZAd25jWQZDZD"
INSTAGRAM_ACCOUNT_ID = "17841465631046584"
TELEGRAM_TOKEN = "8259042725:AAHWIwIOTo4-zCtBL0klgUZ3-O7K0YqYhwc"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# ===== TELEGRAM =====

def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=data, timeout=10)
        return r.ok
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False

def get_updates(offset=0):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    try:
        r = requests.get(url, params={"offset": offset, "timeout": 20}, timeout=25)
        return r.json().get("result", [])
    except:
        return []

def setup_chat_id():
    """Автоматически получает Chat ID при первом запуске"""
    print("\n" + "="*50)
    print("   WISH GRANTER — Первый запуск")
    print("="*50)
    print()
    print("1. Открой Telegram на телефоне или компьютере")
    print("2. Найди бота @annnelll_bot")
    print("3. Напиши ему: /start")
    print()
    print("Ожидаю сообщение от тебя...")
    print()

    last_update_id = 0
    updates = get_updates()
    if updates:
        last_update_id = updates[-1]["update_id"] + 1

    while True:
        updates = get_updates(last_update_id)
        for update in updates:
            last_update_id = update["update_id"] + 1
            if "message" in update:
                chat_id = update["message"]["chat"]["id"]
                name = update["message"]["chat"].get("first_name", "друг")
                print(f"✅ Нашла тебя! Chat ID: {chat_id}")
                # Сохраняем
                with open(CONFIG_FILE, "w") as f:
                    json.dump({"chat_id": chat_id}, f)
                # Приветствие
                send_telegram(chat_id, f"👋 Привет, {name}!\n\n🤖 <b>Wish Granter</b> готов к работе!\n\nКаждое утро в 08:00 я буду присылать тебе:\n📊 Статистику @balazonekz\n💡 Рекомендации что выложить\n⏰ Лучшее время для постов\n\nНапиши /отчет чтобы получить отчёт прямо сейчас!")
                return chat_id
        time.sleep(2)

def load_chat_id():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f).get("chat_id")
    return None

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
        return r.json()
    except:
        return {}

# ===== АНАЛИЗ И ОТЧЁТ =====

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
    day_of_week = now.weekday()
    idea = CONTENT_IDEAS[day_of_week % len(CONTENT_IDEAS)]

    posts = get_recent_posts()
    account = get_account_info()

    followers = account.get("followers_count", "—")
    media_count = account.get("media_count", "—")

    if posts:
        avg_likes = sum(p.get("like_count", 0) for p in posts) / len(posts)
        avg_comments = sum(p.get("comments_count", 0) for p in posts) / len(posts)
        best = max(posts, key=lambda x: x.get("like_count", 0) + x.get("comments_count", 0) * 3)

        # Тип контента лучшего поста
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

    message = f"""🤖 <b>Wish Granter — Ежедневный отчёт</b>
📅 {now.strftime('%d.%m.%Y, %H:%M')}

{stats_text}

💡 <b>Идея контента на сегодня:</b>
{idea}

⏰ <b>Лучшее время для публикации:</b>
12:00–13:00 или 19:00–21:00

#balazone #babybrezza #детскаясмесь #кормлениемладенца"""

    return message

# ===== ОСНОВНОЙ ЦИКЛ =====

def run():
    print("\n🤖 Wish Granter Agent запускается...")

    # Получаем или настраиваем Chat ID
    chat_id = load_chat_id()
    if not chat_id:
        chat_id = setup_chat_id()

    print(f"✅ Chat ID: {chat_id}")
    print("📅 Отчёт будет приходить каждый день в 08:00")
    print("💬 Напиши боту /отчет для немедленного отчёта")
    print("\nАгент работает... (Ctrl+C для остановки)\n")

    last_update_id = 0
    last_report_date = None

    while True:
        now = datetime.now()

        # Проверяем команды от пользователя
        updates = get_updates(last_update_id)
        for update in updates:
            last_update_id = update["update_id"] + 1
            if "message" in update:
                text = update["message"].get("text", "").lower()
                if "/отчет" in text or "/report" in text or "/start" in text:
                    print(f"📨 Запрос отчёта от пользователя")
                    report = make_report()
                    send_telegram(chat_id, report)

        # Ежедневный отчёт в 08:00
        today = now.date()
        if now.hour == 8 and now.minute == 0 and last_report_date != today:
            print(f"📊 Отправляю ежедневный отчёт...")
            report = make_report()
            if send_telegram(chat_id, report):
                last_report_date = today
                print(f"✅ Отчёт отправлен")

        time.sleep(30)

if __name__ == "__main__":
    if "--test" in sys.argv:
        chat_id = load_chat_id()
        if chat_id:
            report = make_report()
            print(report)
            send_telegram(chat_id, report)
            print("✅ Тестовый отчёт отправлен!")
        else:
            print("Сначала запусти: python wish_granter_agent.py")
    else:
        run()
