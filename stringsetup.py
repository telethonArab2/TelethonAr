from telethon.sessions import StringSession
from telethon.sync import TelegramClient

print("""الرجاء الانتقال إلى my.telegram.org
تسجيل الدخول باستخدام حساب Telegram الخاص بك
انقر فوق أدوات تطوير API
إنشاء تطبيق جديد عن طريق إدخال البيانات المطلوبة""")
APP_ID = int(input("Enter APP ID here: "))
API_HASH = input("Enter API HASH here: ")

with TelegramClient(StringSession(), APP_ID, API_HASH) as client:
    print(client.session.save())
    client.send_message("me", client.session.save())