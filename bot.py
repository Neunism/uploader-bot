import os
import ftplib
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import subprocess

# اطلاعات ربات
TELEGRAM_API_TOKEN = '7328102300:AAG-E74QGLOKh9YtdtRbZwtQuUUtYGGt504'

# اطلاعات FTP هاست دانلود
FTP_HOST = '89.235.78.130'
FTP_USER = 'pl.ortatv.fun'
FTP_PASS = 'k7ghB95KaTofWOx4'
FTP_DIR = 'series'  # پوشه مقصد در هاست دانلود

# پوشه محلی برای ذخیره فایل‌ها
DOWNLOAD_DIR = '/tmp/downloads'

# دانلود تورنت با aria2
def download_torrent(torrent_url):
    command = f"aria2c --dir={DOWNLOAD_DIR} {torrent_url}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        return True, None
    else:
        return False, stderr.decode()

# آپلود فایل به هاست FTP
def upload_to_ftp(filename):
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(FTP_DIR)
        
        with open(filename, 'rb') as f:
            ftp.storbinary(f'STOR {os.path.basename(filename)}', f)
        
        ftp.quit()
        return True, None
    except Exception as e:
        return False, str(e)

# دستور شروع ربات
def start(update, context):
    update.message.reply_text("سلام! من یک ربات دانلود تورنت هستم. لطفاً لینک تورنت یا لینک فایل مستقیم را ارسال کنید.")

# دستور دانلود از تورنت
def download(update, context):
    url = " ".join(context.args)
    if not url:
        update.message.reply_text("لطفاً یک لینک تورنت یا لینک فایل مستقیم ارسال کنید.")
        return

    # اگر URL تورنت باشد، دانلود شروع می‌شود
    success, error = download_torrent(url)
    if success:
        # فایل دانلود شده است، حالا آن را آپلود می‌کنیم
        downloaded_file = os.path.join(DOWNLOAD_DIR, os.listdir(DOWNLOAD_DIR)[0])
        success, error = upload_to_ftp(downloaded_file)
        if success:
            update.message.reply_text(f"فایل با موفقیت به هاست آپلود شد: {downloaded_file}")
        else:
            update.message.reply_text(f"خطا در آپلود فایل به هاست: {error}")
    else:
        update.message.reply_text(f"خطا در دانلود تورنت: {error}")

# دستور آپلود فایل مستقیم
def upload_direct(update, context):
    url = " ".join(context.args)
    if not url:
        update.message.reply_text("لطفاً یک لینک فایل مستقیم ارسال کنید.")
        return

    # دانلود فایل از لینک مستقیم
    filename = os.path.join(DOWNLOAD_DIR, url.split('/')[-1])
    os.system(f"curl -o {filename} {url}")
    
    # آپلود به FTP
    success, error = upload_to_ftp(filename)
    if success:
        update.message.reply_text(f"فایل با موفقیت به هاست آپلود شد: {filename}")
    else:
        update.message.reply_text(f"خطا در آپلود فایل به هاست: {error}")

# اجرای ربات
def main():
    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("download", download))  # برای دانلود تورنت
    dp.add_handler(CommandHandler("upload", upload_direct))  # برای آپلود لینک مستقیم

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
