
import ccxt
import pandas as pd
import requests

# بيانات بوت تيليجرام الخاص بك
TELEGRAM_BOT_TOKEN = '8696232395:AAGS80eAVF2QcJkIhgead3rAbpMRQM7SCOs'
TELEGRAM_CHAT_ID = '1039928153'

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    print("Telegram API Response:", response.text) # سيطبع لنا سبب أي مشكلة في السجلات مباشرة

# جلب بيانات Kraken (250 شمعة لحساب المتوسط طويل الأجل)
exchange = ccxt.kraken()
bars = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=250)
df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# حساب المعادلات الإحصائية والمؤشرات
df['SMA_20'] = df['close'].rolling(window=20).mean()
df['Std_20'] = df['close'].rolling(window=20).std()
df['Z_Score'] = (df['close'] - df['SMA_20']) / df['Std_20']

# إضافة فلتر الاتجاه المؤسسي (متوسط 200 شمعة)
df['SMA_200'] = df['close'].rolling(window=200).mean()

latest = df.iloc[-1]
close_price = latest['close']
std = latest['Std_20']
z_score = latest['Z_Score']
sma_200 = latest['SMA_200']

# شروط الدخول مع فلتر الاتجاه المطور:
if z_score < -2 and close_price > sma_200:
    entry = close_price
    stop_loss = close_price - (1.5 * std)
    take_profit = close_price + (3.0 * std)
    
    msg = f"🚀 **فرصة شراء آلي ذكية (Long)**\n\n" \
          f"• نقطة الدخول: `{entry:.2f}$`\n" \
          f"• وقف الخسارة (SL): `{stop_loss:.2f}$`\n" \
          f"• أخذ الربح (TP): `{take_profit:.2f}$`\n" \
          f"• قيمة Z-Score: `{z_score:.2f}`\n" \
          f"• حالة الفلتر: فوق SMA 200 (ترند آمن) ✅"
    send_telegram_alert(msg)

elif z_score > 2 and close_price < sma_200:
    entry = close_price
    stop_loss = close_price + (1.5 * std)
    take_profit = close_price - (3.0 * std)
    
    msg = f"📉 **فرصة بيع آلي ذكية (Short)**\n\n" \
          f"• نقطة الدخول: `{entry:.2f}$`\n" \
          f"• وقف الخسارة (SL): `{stop_loss:.2f}$`\n" \
          f"• أخذ الربح (TP): `{take_profit:.2f}$`\n" \
          f"• قيمة Z-Score: `{z_score:.2f}`\n" \
          f"• حالة الفلتر: تحت SMA 200 (ترند هابط) ✅"
    send_telegram_alert(msg)

else:
    trend_status = "صاعد 📈" if close_price > sma_200 else "هابط 📉"
    status_msg = f"🔍 **تم فحص السوق بنجاح**\n" \
                 f"• السعر: `{close_price:.2f}$`\n" \
                 f"• Z-Score: `{z_score:.2f}`\n" \
                 f"• الاتجاه العام: {trend_status}\n" \
                 f"• الحالة: بانتظار توافق شروط الانحراف والاتجاه معاً."
    send_telegram_alert(status_msg)

print(f"تم فحص السوق بنجاح | السعر: {close_price:.2f} | Z-Score: {z_score:.2f} | الاتجاه: {'صاعد' if close_price > sma_200 else 'هابط'}")
