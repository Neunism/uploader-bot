import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from webtorrent import WebTorrent
import ftplib
import shutil

# متغیرهای محیطی
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')  # توکن ربات تلگرام
FTP_HOST = os.getenv('FTP_HOST')  # آی‌پی هاست FTP
FTP_USER = os.getenv('FTP_USER')  # نام کاربری FTP
FTP_PASS = os.getenv('FTP_PASS')  # پسورد FTP
FTP_TARGET_DIR = os.getenv('FTP_TARGET_DIR')  # پوشه مقصد در هاست FTP

# اتصال به تلگرام
updater = Updater(TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# دانلود تورنت با WebTorrent
def download_torrent(torrent_magnet, file_name):
    client = WebTorrent()
    client.add(torrent_magnet, lambda torrent: torrent.download(file_name))
    print(f"دانلود تورنت {torrent_magnet} با نام {file_name} تکمیل شد.")

# آپلود فایل به هاست FTP
def upload_to_ftp(file_path):
    with ftplib.FTP(FTP_HOST) as ftp:
        ftp.login(FTP_USER, FTP_PASS)
        with open(file_path, 'rb') as file:
            ftp.storbinary(f'STOR {FTP_TARGET_DIR}/{os.path.basename(file_path)}', file)
    print(f"فایل {file_path} به هاست FTP آپلود شد.")

# دستور /start
def start(update, context):
    update.message.reply_text("سلام! برای دانلود تورنت و ارسال فایل‌ها به هاست FTP، لینک تورنت یا فایل را ارسال کنید.")

# دریافت لینک تورنت و دانلود آن
def handle_message(update, context):
    if update.message.text.startswith('magnet:'):
        torrent_magnet = update.message.text
        file_name = 'downloaded_file'  # نام فایل دانلود شده
        update.message.reply_text('در حال دانلود تورنت...')
        download_torrent(torrent_magnet, file_name)
        update.message.reply_text(f'تورنت دانلود شد: {file_name}')

        # آپلود فایل به FTP
        update.message.reply_text('در حال آپلود فایل به هاست...')
        upload_to_ftp(file_name)
        update.message.reply_text(f'فایل به هاست آپلود شد: {file_name}')
        
        # حذف فایل دانلود شده بعد از آپلود
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"فایل {file_name} حذف شد.")

# اتصال دستورات به ربات
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

message_handler = MessageHandler(Filters.text & ~Filters.command, handle_message)
dispatcher.add_handler(message_handler)

# شروع ربات
updater.start_polling()
