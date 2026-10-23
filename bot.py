from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os
import yt_dlp
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8742026471:AAGEMUK-tHljN-NzPpIBxDl6pbcDrBKWn2w"
CHANNEL_USERNAME = "@Alijoychannel" # معرف قناتك الجديد

async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context):
        keyboard = [[InlineKeyboardButton("الاشتراك في القناة أولاً 📢", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("عذراً! يجب عليك الاشتراك في القناة أولاً لاستخدام البوت.", reply_markup=reply_markup)
        return

    # إنشاء قائمة الأزرار السفلية (Menu)
    main_menu = [
        [KeyboardButton("📱 TikTok"), KeyboardButton("📸 Instagram")],
        [KeyboardButton("📘 Facebook"), KeyboardButton("🔴 YouTube")]
    ]
    reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)

    await update.message.reply_text(
        "مرحباً بك! 🎬 أرسل رابط الفيديو مباشرة، أو اختر المنصة من الأزرار بالأسفل لمعرفة كيفية التحميل السريع:",
        reply_markup=reply_markup
    )

async def handle_video_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context):
        keyboard = [[InlineKeyboardButton("الاشتراك في القناة أولاً 📢", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("عذراً! يجب عليك الاشتراك في القناة أولاً لاستخدام البوت.", reply_markup=reply_markup)
        return

    text = update.message.text

    # التحقق إذا ضغط المستخدم على أزرار القائمة
    if text in ["📱 TikTok", "📸 Instagram", "📘 Facebook", "🔴 YouTube"]:
        platform = text.split(" ")[1]
        await update.message.reply_text(
            f"💡 **طريقة التحميل من {platform}:**\n\n"
            f"1. افتح تطبيق {platform}.\n"
            f"2. اضغط على زر **مشاركة (Share)** في الفيديو.\n"
            f"3. اختر **Telegram** ثم اختر هذا البوت.\n"
            f"4. سيتم إرسال الرابط وتحميل الفيديو بدون علامة مائية فوراً!"
        )
        return

    # إذا أرسل المستخدم رابطاً حقيقياً
    if not text.startswith("http"):
        await update.message.reply_text("⚠️ أرجو إرسال رابط صحيح يبدأ بـ http أو اختيار المنصة من الأزرار.")
        return

    await update.message.reply_text("⏳ جاري جلب الفيديو بدون علامة مائية، انتظر قليلاً...")

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'overwrites': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([text])

        with open('video.mp4', 'rb') as video_file:
            await update.message.reply_video(video=video_file)

        os.remove('video.mp4')
    except Exception as e:
        await update.message.reply_text("❌ حدث خطا أثناء تحميل الفيديو، تأكد من صحة الرابط.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video_download))

    # --- سيرفر وهمي لإرضاء منصة Render ومنع مشكلة Port Timeout ---
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is alive!")

    def run_server():
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHandler)
        server.serve_forever()

    threading.Thread(target=run_server, daemon=True).start()

    app.run_polling()
