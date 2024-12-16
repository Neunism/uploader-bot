import os
import ftplib
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Application
from telegram.ext import filters  # تغییر در واردات filters
from telegram.ext import CallbackContext

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
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('سلام! من آماده هستم تا فایل‌ها را دریافت کنم و آپلود کنم.')

# تابع برای ارسال پیام هنگامی که فایل ارسال می‌شود
async def handle_file(update: Update, context: CallbackContext):
    file = update.message.document
    if file:
        file_path = await file.get_file().download()  # استفاده از async برای دانلود فایل
        await update.message.reply_text(f"در حال آپلود فایل {file.file_name} به سرور FTP...")
        
        # ارسال فایل به FTP
        if upload_to_ftp(file_path):
            await update.message.reply_text(f"فایل {file.file_name} با موفقیت آپلود شد!")
        else:
            await update.message.reply_text(f"خطا در آپلود فایل {file.file_name}. لطفاً دوباره امتحان کنید.")
    else:
        await update.message.reply_text("لطفاً یک فایل ارسال کنید.")

# تابع برای تنظیمات و شروع ربات
async def main():
    # استفاده از Application به‌جای Updater
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # دستورات ربات
    application.add_handler(CommandHandler("start", start))
    
    # دریافت فایل‌ها
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))  # تغییر در استفاده از filters
    
    # شروع ربات
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())  # استفاده از asyncio برای اجرای main
