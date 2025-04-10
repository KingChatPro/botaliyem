import telebot
import openai
import sqlite3
from telebot import types
from datetime import datetime
from dotenv import load_dotenv
import os
import requests

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# الحصول على توكن البوت و OpenAI API من المتغيرات البيئية
API_KEY = os.getenv('TELEGRAM_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# تهيئة البوت
bot = telebot.TeleBot(API_KEY)

# تهيئة OpenAI API
openai.api_key = OPENAI_API_KEY

# إنشاء أو الاتصال بقاعدة البيانات
conn = sqlite3.connect('chat_history.db')
cursor = conn.cursor()

# إنشاء جدول لتخزين الرسائل
cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    response TEXT,
    timestamp DATETIME
)''')

# دالة لحفظ الرسائل في قاعدة البيانات
def save_message(user_id, message, response):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO messages (user_id, message, response, timestamp) VALUES (?, ?, ?, ?)", 
                   (user_id, message, response, timestamp))
    conn.commit()

# دالة للحصول على رد من OpenAI
def get_openai_response(user_message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )
    return response.choices[0].message['content']

# دالة لترجمة النصوص بين اللغات
def translate_text(text, target_language="en"):
    url = f"https://api.mymemory.translated.net/get?q={text}&langpair=auto|{target_language}"
    response = requests.get(url).json()
    return response['responseData']['translatedText']

# دالة للحصول على نصائح يومية
def get_daily_tip():
    tips = [
        "ابدأ يومك بشرب كوب من الماء.",
        "حاول دائمًا تحسين مهاراتك باستمرار.",
        "خذ قسطًا من الراحة بين فترات العمل.",
        "الابتسامة هي أفضل طريقة لبدء اليوم."
    ]
    return random.choice(tips)

# دالة لإرسال حالة الطقس باستخدام API خارجي (مثال)
def get_weather():
    # يمكنك استبدال هذه الدالة بتكامل مع API مثل OpenWeatherMap للحصول على حالة الطقس
    return "الطقس اليوم مشمس ودرجة الحرارة 25°C."

# دالة لمعالجة الصور والفيديو
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "لقد أرسلت صورة! يمكنني معالجتها قريبًا.")
    # يمكنك إضافة الكود لتحليل الصورة باستخدام OpenAI أو أدوات أخرى

@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "لقد أرسلت فيديو! يمكنني معالجته قريبًا.")
    # يمكنك إضافة الكود لتحليل الفيديو باستخدام OpenAI أو أدوات أخرى

# التعامل مع الرسائل الواردة
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحبًا! أنا بوت الذكاء الاصطناعي **botaliyem**. كيف يمكنني مساعدتك اليوم؟")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "يمكنك التحدث معي في أي موضوع وسأرد عليك باستخدام الذكاء الاصطناعي. اكتب أي شيء!")

@bot.message_handler(commands=['buttons'])
def send_buttons(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('تعلم البرمجة')
    btn2 = types.KeyboardButton('تحدث معي')
    btn3 = types.KeyboardButton('نصيحة يومية')
    btn4 = types.KeyboardButton('الطقس')
    btn5 = types.KeyboardButton('ترجم النص')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    bot.reply_to(message, "اختر أحد الأزرار:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'تعلم البرمجة')
def learn_programming(message):
    bot.reply_to(message, "رائع! هل ترغب في تعلم لغة Python أو JavaScript؟")

@bot.message_handler(func=lambda message: message.text == 'تحدث معي')
def talk_to_bot(message):
    bot.reply_to(message, "أنا هنا للدردشة معك! اكتب أي شيء.")

@bot.message_handler(func=lambda message: message.text == 'نصيحة يومية')
def daily_tip(message):
    tip = get_daily_tip()
    bot.reply_to(message, f"نصيحة اليوم: {tip}")

@bot.message_handler(func=lambda message: message.text == 'الطقس')
def weather(message):
    weather_info = get_weather()
    bot.reply_to(message, weather_info)

@bot.message_handler(func=lambda message: message.text == 'ترجم النص')
def translate(message):
    bot.reply_to(message, "من فضلك أرسل النص الذي تريد ترجمته.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_message = message.text

    # الحصول على رد من OpenAI
    bot_response = get_openai_response(user_message)

    # حفظ الرسالة والرد في قاعدة البيانات
    save_message(user_id, user_message, bot_response)

    # إرسال الرد للمستخدم
    bot.reply_to(message, bot_response)

# بدء البوت
bot.polling(none_stop=True)
