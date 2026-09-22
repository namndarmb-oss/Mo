import os
import time
import requests

# ۱. دریافت کلید API سایت 5Sim از متغیرهای ایمن گیت‌هاب
API_KEY = os.getenv("dbb3d324f26a4be9a6e07e04db8a4f9a")

if not API_KEY:
    print("❌ خطا: کلید FIVESIM_API_KEY در تنظیمات گیت‌هاب تعریف نشده است.")
    exit(1)

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Accept': 'application/json',
}

# ۲. درخواست خرید شماره مجازی برای تلگرام
# در اینجا کشور را انگلیس (england) انتخاب کردیم، می‌توانید به روسیه (russia) یا کشورهای دیگر تغییر دهید.
print("🚀 در حال درخواست خرید شماره مجازی جدید از پنل 5Sim...")
url_buy = "https://5sim.net"

try:
    response = requests.get(url_buy, headers=headers)
    data = response.json()
except Exception as e:
    print(f"❌ خطا در اتصال به سرور: {e}")
    exit(1)

if response.status_code == 200 and "phone" in data:
    activation_id = data["id"]
    phone_number = data["phone"]
    print("\n" + "="*40)
    print(f"📱 شماره مجازی اختصاصی شما: {phone_number}")
    print("="*40)
    print("🔴 توجه: اکنون شماره را در اپلیکیشن تلگرام خود وارد کنید و دکمه ارسال را بزنید.")
    print("اسکریپت گیت‌هاب منتظر دریافت پیامک فعال‌سازی است...\n")
else:
    print(f"❌ خطا در خرید شماره: {response.text}")
    exit(1)

# ۳. حلقه انتظار برای دریافت پیامک تایید تلگرام
url_check = f"https://5sim.net{activation_id}"

# ۳۰ بار تلاش با فاصله ۱۰ ثانیه (مجموعاً ۵ دقیقه زمان انتظار)
for i in range(30):
    time.sleep(10)
    try:
        check_res = requests.get(url_check, headers=headers).json()
        status = check_res.get("status")
        
        if status == "FINISHED" or (check_res.get("sms") and len(check_res["sms"]) > 0):
            # دریافت آخرین پیامک ارسالی
            sms_data = check_res["sms"][0]
            telegram_code = sms_data["code"]
            print("\n" + "🎉"*10)
            print(f"🔑 کد فعال‌سازی تلگرام دریافت شد: {telegram_code}")
            print(f"💬 متن کامل پیامک: {sms_data['text']}")
            print("🎉"*10)
            break
        elif status == "PENDING":
            print(f"⏳ [{i+1}/30] در حال انتظار... شماره را در تلگرام گوشی وارد کنید.")
        else:
            print(f"وضعیت سفارش: {status}")
    except Exception as e:
        continue
else:
    print("\n❌ زمان انتظار به پایان رسید و کدی دریافت نشد. سفارش لغو شد.")
    # لغو خودکار سفارش در صورت عدم دریافت کد برای بازگشت هزینه به کیف پول شما
    requests.get(f"https://5sim.net{activation_id}", headers=headers)
