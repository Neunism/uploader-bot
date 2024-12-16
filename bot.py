from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import CallbackContext
import os
import ftplib
import aria2p

# توکن ربات تلگرام شما
TELEGRAM_TOKEN = "7328102300:AAG-E74QGLOKh9YtdtRbZwtQuUUtYGGt504"

# اطلاعات FTP
FTP_HOST = "89.235.78.130"
FTP_USER = "pl.ortatv.fun"
FTP_PASS = "k7ghB95KaTofWOx4"
FTP_TARGET_DIR = "/series"

# پیکربندی aria2
aria2 = aria2p.API(aria2p.Client(
    host="http://127.0.0.1:6800/jsonrpc",  # آدرس سرور aria2
    secret=""
))

# تابع شروع ربات
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("سلام! من آماده‌ام که به شما کمک کنم. لطفاً یک لینک تورنت یا لینک مستقیم ارسال کنید.")

# تابع برای پردازش لینک‌ها (تورنت یا مستقیم)
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text

    # اگر لینک تورنت است
    if text.endswith(".torrent"):
        await update.message.reply_text("در حال دانلود فایل تورنت...")
        download_torrent(text, update)
    # اگر لینک مستقیم است
    elif text.startswith("http"):
        await update.message.reply_text("در حال دانلود فایل از لینک مستقیم...")
        download_direct_link(text, update)
    else:
        await update.message.reply_text("لطفاً یک لینک تورنت یا لینک مستقیم معتبر ارسال کنید.")

# دانلود تورنت با aria2
def download_torrent(torrent_url: str, update: Update):
    try:
        # دانلود تورنت با aria2
        download = aria2.add_torrent(torrent_url)
        file_path = download.files[0].path

        # آپلود فایل به هاست دانلود
        upload_to_ftp(file_path, update)
    except Exception as e:
        update.message.reply_text(f"خطا در دانلود تورنت: {str(e)}")

# دانلود لینک مستقیم و آپلود به FTP
def download_direct_link(url: str, update: Update):
    try:
        # دانلود فایل از لینک مستقیم
        file_name = url.split("/")[-1]
        download_path = os.path.join("/tmp", file_name)

        os.system(f"curl -L {url} -o {download_path}")

        # آپلود فایل به هاست دانلود
        upload_to_ftp(download_path, update)
    except Exception as e:
        update.message.reply_text(f"خطا در دانلود لینک مستقیم: {str(e)}")

# آپلود فایل به هاست FTP
def upload_to_ftp(file_path: str, update: Update):
    try:
        # اتصال به FTP
        with ftplib.FTP(FTP_HOST) as ftp:
            ftp.login(FTP_USER, FTP_PASS)

            # تغییر به دایرکتوری مقصد
            ftp.cwd(FTP_TARGET_DIR)

            # آپلود فایل
            with open(file_path, "rb") as file:
                ftp.storbinary(f"STOR {os.path.basename(file_path)}", file)

        update.message.reply_text(f"فایل با موفقیت به هاست دانلود آپلود شد: {os.path.basename(file_path)}")
    except Exception as e:
        update.message.reply_text(f"خطا در آپلود به FTP: {str(e)}")

# تابع اصلی برنامه
def main():
    # ایجاد و راه‌اندازی ربات
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # دستورات
    application.add_handler(CommandHandler("start", start))

    # پیام‌ها
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # شروع ربات
    application.run_polling()

if __name__ == '__main__':
    main()
