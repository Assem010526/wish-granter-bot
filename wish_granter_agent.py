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
CHAT_ID = 446497122

app = Flask(__name__)

# ===== TELEGRAM =====

def send_telegram(message, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    if reply_markup:
        data["reply_markup"] = reply_markup
    try:
        r = requests.post(url, json=data, timeout=10)
        return r.ok
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False

def answer_callback(callback_query_id, text="✅"):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery"
    requests.post(url, json={"callback_query_id": callback_query_id, "text": text}, timeout=5)

# ===== INSTAGRAM =====

def get_ig_account_id():
    global INSTAGRAM_ACCOUNT_ID
    try:
        r = requests.get(
            "https://graph.facebook.com/v20.0/me/accounts",
            params={"access_token": INSTAGRAM_TOKEN, "fields": "id,name,instagram_business_account"},
            timeout=10
        )
        pages = r.json().get("data", [])
        for page in pages:
            ig = page.get("instagram_business_account")
            if ig:
                INSTAGRAM_ACCOUNT_ID = ig["id"]
                return ig["id"]
    except Exception as e:
        print(f"Ошибка получения IG ID: {e}")
    return INSTAGRAM_ACCOUNT_ID

def get_recent_posts():
    ig_id = get_ig_account_id()
    url = f"https://graph.facebook.com/v20.0/{ig_id}/media"
    params = {
        "access_token": INSTAGRAM_TOKEN,
        "fields": "id,caption,media_type,timestamp,like_count,comments_count,permalink",
        "limit": 12
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.json().get("data", [])
    except Exception as e:
        print(f"Ошибка Instagram media API: {e}")
        return []

def get_account_info():
    ig_id = get_ig_account_id()
    url = f"https://graph.facebook.com/v20.0/{ig_id}"
    params = {
        "access_token": INSTAGRAM_TOKEN,
        "fields": "followers_count,media_count,name,biography"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.json()
    except Exception as e:
        print(f"Ошибка Instagram account API: {e}")
        return {}

def get_recent_comments():
    ig_id = get_ig_account_id()
    try:
        r = requests.get(
            f"https://graph.facebook.com/v20.0/{ig_id}/media",
            params={"access_token": INSTAGRAM_TOKEN, "fields": "id,comments_count,permalink", "limit": 5},
            timeout=10
        )
        posts = r.json().get("data", [])
        comments_info = []
        for post in posts:
            if post.get("comments_count", 0) > 0:
                cr = requests.get(
                    f"https://graph.facebook.com/v20.0/{post['id']}/comments",
                    params={"access_token": INSTAGRAM_TOKEN, "fields": "from,text,timestamp", "limit": 5},
                    timeout=10
                )
                for c in cr.json().get("data", []):
                    comments_info.append({
                        "post_url": post.get("permalink", ""),
                        "user": c.get("from", {}).get("name", "Неизвестно"),
                        "text": c.get("text", "")[:100]
                    })
        return comments_info[:5]
    except Exception as e:
        print(f"Ошибка получения комментариев: {e}")
        return []

# ===== КОНТЕНТ =====

VIDEO_IDEAS = [
    {
        "title": "🎬 30 секунд магии Balazone",
        "idea": "Покажи как аппарат за 30 секунд готовит идеальную смесь",
        "steps": [
            "1️⃣ Скачай трендовый звук с TikTok (ищи #babyformula или #babyhack)",
            "2️⃣ Сними крупным планом: засыпаешь мерку → нажимаешь кнопку → готовая смесь",
            "3️⃣ Обработай в CapCut: добавь замедление на момент готовой бутылочки",
            "4️⃣ Текст на экране: «30 секунд vs 5 минут вручную 😴»",
            "5️⃣ Опубликуй в 19:00-21:00, хештеги: #babybrezza #balazone #детскоепитание"
        ],
        "source": "TikTok → поиск: baby formula machine | YouTube → 'Baby Brezza review'"
    },
    {
        "title": "👶 До/После — реакция мамы",
        "idea": "Покажи контраст: усталая мама ночью вручную vs мама с Balazone спокойно спит",
        "steps": [
            "1️⃣ Найди трендовый звук 'transformation' на TikTok или Reels",
            "2️⃣ Часть 1: сними как ты долго мешаешь смесь ночью (усталый вид)",
            "3️⃣ Часть 2 (резкая смена): нажала кнопку — улыбаешься — идёшь спать",
            "4️⃣ В CapCut используй эффект 'zoom' на переходе",
            "5️⃣ Подпись: «Этот аппарат вернул мне сон 😭❤️»"
        ],
        "source": "TikTok → поиск: mom transformation | CapCut → шаблоны Before/After"
    },
    {
        "title": "📦 Распаковка с WOW-эффектом",
        "idea": "Распакуй коробку как будто это подарок мечты",
        "steps": [
            "1️⃣ Скачай звук 'unboxing' с TikTok или используй ASMR музыку",
            "2️⃣ Сними сверху: коробка → открываешь → каждый элемент отдельно",
            "3️⃣ Крупный план на логотип Balazone, на кнопки, на экран",
            "4️⃣ В CapCut добавь текст для каждого элемента что он делает",
            "5️⃣ Финал: работающий аппарат + текст «Уже на Kaspi 🛒»"
        ],
        "source": "TikTok → поиск: unboxing baby | YouTube → распаковка Baby Brezza"
    },
    {
        "title": "💬 Отзыв настоящей мамы",
        "idea": "Живой отзыв покупательницы прямо в видео",
        "steps": [
            "1️⃣ Попроси 2-3 покупательниц записать 15-секундное видео с ребёнком",
            "2️⃣ Попроси сказать: имя, сколько месяцев ребёнку, что понравилось",
            "3️⃣ Смонтируй в CapCut: их видео + субтитры их слов",
            "4️⃣ Добавь текст: «Реальный отзыв, не реклама ❤️»",
            "5️⃣ Опубликуй в понедельник утром 12:00 — максимальный охват"
        ],
        "source": "Попроси покупательниц в директ | Kaspi отзывы → скриншот + озвучка"
    },
    {
        "title": "🔄 Сравнение: Balazone vs вручную",
        "idea": "Засеки время: 30 сек vs 5 минут — покажи разницу",
        "steps": [
            "1️⃣ Используй split-screen в CapCut (два экрана рядом)",
            "2️⃣ Левый экран: мама мешает вручную с таймером",
            "3️⃣ Правый экран: Balazone уже готов пока она ещё мешает",
            "4️⃣ Добавь смешной звук или 'минус 5 лет жизни' эффект",
            "5️⃣ Финал: Balazone выигрывает → текст «Выбор очевиден 😄»"
        ],
        "source": "CapCut → шаблон Split Screen | TikTok → звук 'comparison'"
    },
    {
        "title": "🎯 Факт который удивит",
        "idea": "Интересный факт о детском питании + почему температура важна",
        "steps": [
            "1️⃣ Факт: «При температуре выше 70°C теряются витамины» — сними текст",
            "2️⃣ Покажи термометром: вода из чайника vs Balazone (точно 37°C)",
            "3️⃣ Добавь врача или статью в качестве источника (скриншот)",
            "4️⃣ В CapCut используй анимированный текст для цифр",
            "5️⃣ Хештеги: #детскоепитание #здоровьемалыша #казахстан"
        ],
        "source": "Google: 'температура детской смеси норма' | ВОЗ рекомендации"
    },
    {
        "title": "🛒 Как купить на Kaspi",
        "idea": "Пошаговое видео — как найти и купить Balazone на Kaspi за 1 минуту",
        "steps": [
            "1️⃣ Запись экрана телефона: открываешь Kaspi → вводишь Balazone",
            "2️⃣ Показываешь рейтинг, отзывы, кнопку заказа",
            "3️⃣ Добавь текст: «Доставка за 1-2 дня по Казахстану»",
            "4️⃣ Финальный кадр: аппарат + «Ссылка в шапке профиля»",
            "5️⃣ Опубликуй в пятницу вечером — люди планируют покупки"
        ],
        "source": "Запись экрана (встроенная функция iPhone/Android)"
    },
    {
        "title": "❓ Вопрос-ответ в сторис",
        "idea": "Ответь на 3 самых частых вопроса о Balazone",
        "steps": [
            "1️⃣ Открой Instagram → Сторис → наклейка «Вопрос»",
            "2️⃣ Напиши: «Спрашивайте всё о Balazone — отвечу!»",
            "3️⃣ Собери вопросы за 24 часа",
            "4️⃣ Сними видео-ответы: держишь аппарат и отвечаешь",
            "5️⃣ Выложи серию Reels: каждый вопрос = отдельное 15-сек видео"
        ],
        "source": "Вопросы из директа и комментариев | Kaspi отзывы — частые вопросы"
    },
]

SALES_PRACTICES = """💼 <b>Мировые практики продаж для Balazone:</b>

<b>📱 Когда публиковать:</b>
• Пн-Пт: 12:00-13:00 (обеденный перерыв мам)
• Вечер: 19:00-21:00 (дети уснули, мамы в телефоне)
• Выходные: 10:00-12:00 (утро без спешки)

<b>💬 Какие комментарии писать под чужими постами:</b>
• Под постами о детях/материнстве: «Как вы справляетесь с ночными кормлениями? 🌙»
• Под постами мам: «У нас есть решение для ночных кормлений — сэкономит часы 💙»
• НЕ пиши сразу рекламу — сначала 3 искренних комментария, потом продукт

<b>📊 Формула контента 70/20/10:</b>
• 70% — полезный контент (советы, факты о детском питании)
• 20% — отзывы и истории покупателей
• 10% — прямая реклама и акции

<b>🎯 Триггеры покупки:</b>
• Страх: «Знаете ли вы что смесь теряет витамины при неправильной температуре?»
• Удобство: «Ночное кормление за 30 секунд пока муж спит»
• Социальное доказательство: «Уже 500+ казахстанских мам выбрали Balazone»

<b>📞 Скрипт для директа:</b>
Когда пишут «сколько стоит?» →
«Привет! Аппарат стоит [цена]. Он готовит смесь точной температуры за 30 сек, экономит ~2 часа в сутки. Есть на Kaspi с доставкой завтра. Оформить? 😊»"""

MARKET_ANALYSIS = """📊 <b>Анализ рынка: что хорошо продаётся рядом с Balazone:</b>

<b>🔥 Топ сопутствующих товаров в Казахстане:</b>
• Детские смеси (NAN, Similac, Nutrilak) — предложи как партнёрство
• Бутылочки с антиколиковой системой (Philips Avent, Dr.Brown's)
• Стерилизаторы бутылочек
• Ночники для детской
• Слинги и эрго-рюкзаки

<b>📈 Тренды 2024-2025 (baby-рынок Казахстан):</b>
• Органические смеси растут +40% в год
• Умные гаджеты для ухода за ребёнком — главный тренд
• Казахстанские мамы активно покупают в Kaspi (60% онлайн-покупок)
• Instagram Reels даёт x3 охват vs обычные посты

<b>💡 Идеи для роста продаж:</b>
• Пакет «Молодой маме»: Balazone + смесь на 1 месяц
• Реферальная программа: приведи подругу — скидка обеим
• Партнёрство с роддомами и детскими клиниками
• Бесплатная демонстрация в детских магазинах

<b>🎁 Лучшие акции для Казахстана:</b>
• Скидка на День матери (ноябрь)
• Новогодние комплекты (декабрь — пик продаж)
• Акция «Купи сейчас — плати через месяц» через Kaspi рассрочку"""

CONTACTS_SCRIPT = """📞 <b>Кому звонить и предлагать сотрудничество:</b>

<b>🏥 Медицинские учреждения:</b>
• Роддома Алматы/Астаны — предложи демонстрацию для молодых мам
• Педиатрические клиники — реклама в зале ожидания
• Скрипт: «Здравствуйте, я представляю аппарат Balazone для приготовления детской смеси. Могли бы мы разместить информацию для ваших пациентов?»

<b>🛍️ Детские магазины и ТРЦ:</b>
• Mothercare, Dочки-Cочки, Baby Boom в вашем городе
• Скрипт: «Добрый день! Хотим предложить совместную акцию/выставку нашего продукта в вашем магазине»

<b>👩‍💻 Instagram блогеры-мамы Казахстана:</b>
• Ищи по хештегам: #казахстанскаямама #алматымама #астанамама
• Критерии: 5,000-50,000 подписчиков, высокий % комментариев
• Предложи: бесплатный аппарат в обмен на честный обзор

<b>🤝 Как найти контакты:</b>
• 2GIS → «роддомы», «детские клиники» → телефоны
• Instagram → хештег #казахстанскаямама → DM блогерам
• Kaspi продавцы детских товаров → предложи перекрёстную рекламу

<b>📝 Шаблон письма блогеру:</b>
«Привет [имя]! Я вижу что твои подписчики — молодые мамы. У нас есть аппарат Balazone который готовит смесь за 30 секунд. Хотим подарить тебе для честного обзора. Интересно?»"""

MOTIVATIONS = [
    "🔥 Каждый «нет» приближает тебя к «да». Продолжай — результат уже близко!",
    "💪 Малый бизнес — это марафон, не спринт. Ты уже на дистанции!",
    "🌟 Одна правильная публикация может изменить всё. Сегодня может быть тот самый день!",
    "🚀 Твой продукт реально помогает мамам. Каждая продажа — это облегчение для семьи!",
    "💎 Успешные предприниматели делают то, что другие откладывают. Ты уже делаешь!",
    "❤️ Каждый подписчик — потенциальный покупатель. Каждый покупатель — ходячая реклама!",
    "🎯 Фокус на одном действии сегодня: сними одно видео. Одно видео = сотни просмотров!",
    "🌈 Конкуренты видят тренды. Лидеры создают тренды. Стань лидером детского рынка Казахстана!",
]

# ===== КЛАВИАТУРЫ =====

def main_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "📊 Отчёт", "callback_data": "report"},
                {"text": "🎬 Идея видео", "callback_data": "video"}
            ],
            [
                {"text": "💼 Практики продаж", "callback_data": "sales"},
                {"text": "📈 Анализ рынка", "callback_data": "market"}
            ],
            [
                {"text": "📞 Контакты партнёров", "callback_data": "contacts"},
                {"text": "💬 Комментарии", "callback_data": "comments"}
            ],
            [
                {"text": "🔥 Мотивация", "callback_data": "motivation"}
            ]
        ]
    }

# ===== ОТЧЁТ =====

def make_report():
    now = datetime.now()
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
        best_caption = (best.get("caption", "") or "")[:80]

        stats_text = f"""📈 <b>Статистика @balazonekz:</b>
• Подписчиков: <b>{followers}</b>
• Всего постов: {media_count}
• Среднее лайков: {avg_likes:.0f}
• Среднее комментариев: {avg_comments:.1f}

🏆 <b>Лучший пост:</b>
• Тип: {type_ru}
• ❤️ {best.get('like_count', 0)} лайков | 💬 {best.get('comments_count', 0)} комментариев
• Дата: {best_date}
• «{best_caption}...»"""
    else:
        stats_text = f"📈 Подписчиков: <b>{followers}</b> | Постов: {media_count}"

    idx = now.weekday()
    idea = VIDEO_IDEAS[idx % len(VIDEO_IDEAS)]
    motivation = MOTIVATIONS[now.day % len(MOTIVATIONS)]

    return f"""🤖 <b>Wish Granter — Ежедневный отчёт</b>
📅 {now.strftime('%d.%m.%Y, %H:%M')}

{stats_text}

💡 <b>Идея видео на сегодня:</b>
{idea['title']} — {idea['idea']}

⏰ <b>Лучшее время для публикации:</b>
12:00–13:00 или 19:00–21:00

✨ <b>Мотивация дня:</b>
{motivation}

#balazone #babybrezza #детскаясмесь #казахстан"""

def make_video_idea():
    now = datetime.now()
    idea = VIDEO_IDEAS[now.weekday() % len(VIDEO_IDEAS)]
    steps_text = "\n".join(idea["steps"])
    return f"""{idea['title']}

<b>Идея:</b> {idea['idea']}

<b>Пошаговая инструкция:</b>
{steps_text}

<b>📲 Где найти материал:</b>
{idea['source']}

<b>🛠 Приложения для монтажа:</b>
• CapCut (бесплатно, iOS/Android) — лучший выбор
• InShot — простой монтаж
• Instagram встроенный редактор

<b>⏰ Когда публиковать:</b> сегодня в 19:00-21:00"""

# ===== FLASK ENDPOINTS =====

@app.route("/", methods=["GET"])
def home():
    return "Wish Granter Bot is running! 🤖"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({"ok": True})

    # Обработка callback кнопок
    if "callback_query" in data:
        cb = data["callback_query"]
        cb_data = cb.get("data", "")
        cb_id = cb["id"]
        chat_id = cb["message"]["chat"]["id"]

        if chat_id == CHAT_ID:
            answer_callback(cb_id)
            if cb_data == "report":
                report = make_report()
                send_telegram(report, main_keyboard())
            elif cb_data == "video":
                send_telegram(make_video_idea(), main_keyboard())
            elif cb_data == "sales":
                send_telegram(SALES_PRACTICES, main_keyboard())
            elif cb_data == "market":
                send_telegram(MARKET_ANALYSIS, main_keyboard())
            elif cb_data == "contacts":
                send_telegram(CONTACTS_SCRIPT, main_keyboard())
            elif cb_data == "motivation":
                motivation = MOTIVATIONS[datetime.now().day % len(MOTIVATIONS)]
                send_telegram(f"🔥 <b>Мотивация дня:</b>\n\n{motivation}", main_keyboard())
            elif cb_data == "comments":
                comments = get_recent_comments()
                if comments:
                    text = "💬 <b>Последние комментарии:</b>\n\n"
                    for c in comments:
                        text += f"👤 <b>{c['user']}</b>: {c['text']}\n📎 {c['post_url']}\n\n"
                else:
                    text = "💬 Комментариев пока нет или нет доступа."
                send_telegram(text, main_keyboard())

        return jsonify({"ok": True})

    # Обработка текстовых сообщений
    if "message" in data:
        text = data["message"].get("text", "").lower()
        chat_id_incoming = data["message"]["chat"]["id"]

        if chat_id_incoming == CHAT_ID:
            if "debug" in text:
                r1 = requests.get("https://graph.facebook.com/v20.0/me",
                    params={"access_token": INSTAGRAM_TOKEN, "fields": "id,name"}, timeout=10)
                send_telegram(f"Me:\n{r1.text[:500]}")
                r2 = requests.get("https://graph.facebook.com/v20.0/me/instagram_accounts",
                    params={"access_token": INSTAGRAM_TOKEN, "fields": "id,username,followers_count,media_count"}, timeout=10)
                send_telegram(f"IG accounts:\n{r2.text[:800]}")
                r3 = requests.get("https://graph.facebook.com/v20.0/me/accounts",
                    params={"access_token": INSTAGRAM_TOKEN, "fields": "id,name,instagram_business_account{id,username,followers_count}"}, timeout=10)
                send_telegram(f"Pages+IG:\n{r3.text[:800]}")
            elif "/start" in text:
                welcome = """🤖 <b>Wish Granter — твой бизнес-помощник!</b>

Привет, Асем! Я помогу тебе развивать @balazonekz 🚀

Что я умею:
📊 Показывать статистику Instagram
🎬 Давать идеи видео с пошаговыми инструкциями
💼 Рассказывать практики продаж
📈 Анализировать рынок
📞 Находить контакты для партнёрства
🔥 Мотивировать каждый день

Выбери что тебя интересует 👇"""
                send_telegram(welcome, main_keyboard())
            elif "отчет" in text or "отчёт" in text or "/report" in text:
                report = make_report()
                send_telegram(report, main_keyboard())
            elif "видео" in text or "video" in text:
                send_telegram(make_video_idea(), main_keyboard())
            elif "продаж" in text or "sales" in text:
                send_telegram(SALES_PRACTICES, main_keyboard())
            elif "рынок" in text or "анализ" in text:
                send_telegram(MARKET_ANALYSIS, main_keyboard())
            elif "контакт" in text or "звонить" in text:
                send_telegram(CONTACTS_SCRIPT, main_keyboard())
            elif "мотив" in text:
                motivation = MOTIVATIONS[datetime.now().day % len(MOTIVATIONS)]
                send_telegram(f"🔥 <b>Мотивация дня:</b>\n\n{motivation}", main_keyboard())
            else:
                send_telegram("Выбери действие 👇", main_keyboard())

    return jsonify({"ok": True})

@app.route("/trigger_report", methods=["GET", "POST"])
def trigger_report():
    """Cron-job.org вызывает этот URL каждый день в 08:00"""
    report = make_report()
    success = send_telegram(report, main_keyboard())
    return jsonify({"ok": success, "time": datetime.now().isoformat()})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🤖 Wish Granter запускается на порту {port}...")
    app.run(host="0.0.0.0", port=port)
