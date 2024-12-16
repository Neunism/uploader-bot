import os
import ftplib
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters  # تغییر در واردات Filters

# توکن ربات تلگرام خود را وارد کنید
TELEGRAM_TOKEN = '7328102300:AAG-E74QGLOKh9YtdtRbZwtQuUUtYGGt504'  # توکن ربات شما

# اطلاعات FTP
FTP_HOST = "89.235.78.130"
FTP_USER = "pl.ortatv.fun"
FTP_PASS = "k7ghB95KaTofWOx4"
FTP_DIR = "/series"

# تابع برای آپلود فایل به سرور FTP
def upload_to_ftp(file_path: str):
    try:
        with ftplib.FTP(FTP_HOST) as ftp:
            ftp.login(FTP_USER, FTP_PASS)
            with open(file_path, "rb") as file:
                ftp.cwd(FTP_DIR)
                ftp.storbinary(f"STOR {os.path.basename(file_path)}", file)
        return True
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False

# تابع برای شروع کار ربات
def start(update: Update, context: CallbackContext):
    update.message.reply_text('سلام! من آماده هستم تا فایل‌ها را دریافت کنم و آپلود کنم.')

# تابع برای ارسال پیام هنگامی که فایل ارسال می‌شود
def handle_file(update: Update, context: CallbackContext):
    file = update.message.document
    if file:
        file_path = file.get_file().download()
        update.message.reply_text(f"در حال آپلود فایل {file.file_name} به سرور FTP...")
        
        # ارسال فایل به FTP
        if upload_to_ftp(file_path):
            update.message.reply_text(f"فایل {file.file_name} با موفقیت آپلود شد!")
        else:
            update.message.reply_text(f"خطا در آپلود فایل {file.file_name}. لطفاً دوباره امتحان کنید.")
    else:
        update.message.reply_text("لطفاً یک فایل ارسال کنید.")

# تابع برای تنظیمات و شروع ربات
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # دستورات ربات
    dp.add_handler(CommandHandler("start", start))
    
    # دریافت فایل‌ها
    dp.add_handler(MessageHandler(filters.Document.ALL, handle_file))  # تغییر در استفاده از filters
    
    # شروع ربات
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
