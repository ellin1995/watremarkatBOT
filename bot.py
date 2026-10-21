import os
import yt_dlp
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8742026471:AAGEMMK-tHijI-NzPpIBeDi6pbcDrBk4N2w"
CHANNEL_USERNAME = "@alijoychannel"  # معرف قناتك الجديد

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
        await update.message.reply_text("عذراً! يجب عليك الاشتراك في القناة أولاً لاستخدام البوت:", reply_markup=reply_markup)
        return

    await update.message.reply_text("مرحباً بك! أرسل لي رابط الفيديو وسأقوم بتحميله وإرساله لك بدون علامة مائية.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context):
        keyboard = [[InlineKeyboardButton("اشترك في القناة أولاً 📢", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("عذراً! يجب عليك الاشتراك في القناة لاستخدام البوت:", reply_markup=reply_markup)
        return

    url = update.message.text
    if not url.startswith("http"):
        await update.message.reply_text("الرجاء إرسال رابط صحيح يبدأ بـ http")
        return

    await update.message.reply_text("جاري جلب الفيديو بدون علامة مائية، انتظر قليلاً...")
    
    # تحميل الفيديو باستخدام yt-dlp وإرساله
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'nooverwrites': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        with open('video.mp4', 'rb') as video_file:
            await update.message.reply_video(video=video_file)
            
        os.remove('video.mp4')
    except Exception as e:
        await update.message.reply_text("حدث خطأ أثناء تحميل الفيديو. تأكد من صحة الرابط.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))

if __name__ == "__main__":
    app.run_polling()
