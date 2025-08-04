import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai
from gtts import gTTS
import os

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Токены берём из переменных окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

openai.api_key = OPENAI_API_KEY

# Перевод текста
async def translate_text(text, target_lang="тайский язык"):
    prompt = f"Переведи этот текст на {target_lang}: {text}"
    response = openai.ChatCompletion.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# Обработка текстовых сообщений
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Определяем язык (если есть тайские буквы — переводим на русский)
    if any('\u0E00' <= ch <= '\u0E7F' for ch in user_text):
        target = "русский язык"
        voice_lang = "ru"
    else:
        target = "тайский язык"
        voice_lang = "th"

    translation = await translate_text(user_text, target)

    # Озвучка результата
    tts = gTTS(text=translation, lang=voice_lang)
    tts.save("result.mp3")

    await update.message.reply_text(translation)
    await update.message.reply_voice(voice=open("result.mp3", "rb"))

# Приветственное сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я переводчик 🇷🇺 ↔ 🇹🇭. Напиши сообщение, и я переведу его.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
