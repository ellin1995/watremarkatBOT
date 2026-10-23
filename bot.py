import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import edge_tts

TOKEN = os.environ.get("BOT_TOKEN") or "8846303152:AAEmzh1yC2WKIFC1SnEzQNtoqS8Rltk0jXk"
CHANNEL_USERNAME = "@txttospeechali"

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"TTS Bot is Running Successfully!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

Threading.Thread(target=run_server, daemon=True).start()

async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context):
        keyboard = [[InlineKeyboardButton("اشترك في القناة أولاً 📢", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("عذراً! يجب عليك الاشتراك في القناة أولاً لاستخدام البوت.", reply_markup=reply_markup)
        return

    await update.message.reply_text(
        "أهلاً بك في بوت تحويل النص إلى صوت! 🎙️\n\nأرسل لي أي نص باللغة العربية أو الإنجليزية وسأقوم بتحويله إلى رسالة صوتية بجودة عالية فوراً."
    )

async def handle_tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context):
        keyboard = [[InlineKeyboardButton("اشترك في القناة أولاً 📢", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("عذراً! يجب عليك الاشتراك في القناة أولاً لاستخدام البوت.", reply_markup=reply_markup)
        return

    text = update.message.text
    await update.message.reply_text("جارٍ تحويل النص إلى صوت... ⏳")

    try:
        output_file = "voice.mp3"
        voice = "ar-EG-SalmaNeural"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)

        with open(output_file, 'rb') as audio:
            await update.message.reply_voice(voice=audio, caption="تم تحويل النص بنجاح ✨")

        os.remove(output_file)
    except Exception as e:
        await update.message.reply_text("حدث خطا أثناء تحويل النص إلى صوت، حاول مجدداً ❌")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tts))
    app.run_polling()

if __name__ == '__main__':
    main()
