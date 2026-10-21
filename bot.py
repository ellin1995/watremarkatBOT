import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# توكن البوت الجديد الخاص بك
TOKEN = "8742026471:AAGEMMK-tHijI-NzPpIBeDi6pbcDrBk4N2w"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً بك! أرسل لي رابط الفيديو وسأقوم بتحميله وإرساله لك بدون علامة مائية.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"):
        await update.message.reply_text("الرجاء إرسال رابط صحيح يبدأ بـ http")
        return

    await update.message.reply_text("⏳ جاري جلب الفيديو بدون علامة مائية، انتظر قليلاً...")

    chat_id = update.message.chat_id
    output_template = f"video_{chat_id}.mp4"

    ydl_opts = {
        'outtmpl': output_template,
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(output_template):
            with open(output_template, 'rb') as video_file:
                await update.message.reply_video(video=video_file)
            os.remove(output_template)
        else:
            await update.message.reply_text("عذراً، لم أتمكن من العثور على الفيديو المُحمل.")

    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء تحميل الفيديو: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))

    print("البوت يعمل الآن...")
    app.run_polling()