import os
import ftplib
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# اطلاعات FTP شما
FTP_HOST = "89.235.78.130"
FTP_USERNAME = "pl.ortatv.fun"
FTP_PASSWORD = "k7ghB95KaTofWOx4"
FTP_DEST_DIR = "/series"  # پوشه مقصد در هاست

# فعال کردن لاگینگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    """پیام خوش‌آمدگویی"""
    update.message.reply_text("سلام! من یک ربات هستم. لطفاً لینک مستقیم فایل را ارسال کن تا آن را به هاست آپلود کنم.")

def handle_message(update: Update, context: CallbackContext):
    """وقتی که پیام حاوی لینک مستقیم باشد"""
    url = update.message.text
    
    # بررسی لینک
    if url.startswith("http://") or url.startswith("https://"):
        update.message.reply_text(f"در حال آپلود فایل از لینک: {url}")
        
        try:
            # آپلود فایل
            upload_to_ftp(url)
            update.message.reply_text("آپلود فایل با موفقیت انجام شد!")
        except Exception as e:
            update.message.reply_text(f"خطا در آپلود فایل: {e}")
    else:
        update.message.reply_text("این لینک معتبر نیست. لطفاً یک لینک مستقیم ارسال کنید.")

def upload_to_ftp(url: str):
    """آپلود فایل به هاست FTP"""
    
    # اتصال به FTP
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USERNAME, FTP_PASSWORD)
    
    # دریافت فایل از URL
    local_filename = url.split("/")[-1]  # نام فایل را از URL استخراج می‌کنیم
    with open(local_filename, 'wb') as f:
        f.write(requests.get(url).content)

    # آپلود به FTP
    with open(local_filename, 'rb') as file:
        ftp.cwd(FTP_DEST_DIR)  # پوشه مقصد
        ftp.storbinary(f"STOR {local_filename}", file)

    # بستن اتصال FTP
    ftp.quit()

    # حذف فایل محلی پس از آپلود
    os.remove(local_filename)

def main():
    """راه‌اندازی ربات"""
    
    # توکن ربات
    TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
    
    # راه‌اندازی ربات
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # تنظیم دستور start
    dispatcher.add_handler(CommandHandler("start", start))

    # تنظیم دریافت پیام‌ها و بررسی لینک‌ها
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # شروع ربات
    updater.start_polling()

    # اجرای ربات تا زمانی که خاموش نشود
    updater.idle()

if __name__ == '__main__':
    main()
