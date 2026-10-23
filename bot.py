
import ccxt
import pandas as pd
import requests

# بيانات بوت تيليجرام الخاص بك
TELEGRAM_BOT_TOKEN = '8696232395:AAGS80eAVF2QcJk8hgead3rAbpWRQM7SC0s'
TELEGRAM_CHAT_ID = '1039928153'

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

# الاتصال بـ Kraken وجلب البيانات
exchange = ccxt.kraken()
bars = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=100)
df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# حساب المعادلات الإحصائية
df['SMA_20'] = df['close'].rolling(window=20).mean()
df['Std_20'] = df['close'].rolling(window=20).std()
df['Z_Score'] = (df['close'] - df['SMA_20']) / df['Std_20']

latest = df.iloc[-1]
close_price = latest['close']
std = latest['Std_20']
z_score = latest['Z_Score']

# التحقق من الإشارات وإرسالها فوراً
if z_score < -2:
    entry = close_price
    stop_loss = close_price - (1.5 * std)
    take_profit = close_price + (3.0 * std)
    
    msg = f"🚨 *فرصة شراء آلي (Long)*\n\n" \
          f"• نقطة الدخول: `{entry:.2f}$`\n" \
          f"• وقف الخسارة (SL): `{stop_loss:.2f}$`\n" \
          f"• أخذ الربح (TP): `{take_profit:.2f}$`\n" \
          f"• قيمة Z-Score: `{z_score:.2f}`"
    send_telegram_alert(msg)

elif z_score > 2:
    entry = close_price
    stop_loss = close_price + (1.5 * std)
    take_profit = close_price - (3.0 * std)
    
    msg = f"🚨 *فرصة بيع آلي (Short)*\n\n" \
          f"• نقطة الدخول: `{entry:.2f}$`\n" \
          f"• وقف الخسارة (SL): `{stop_loss:.2f}$`\n" \
          f"• أخذ الربح (TP): `{take_profit:.2f}$`\n" \
          f"• قيمة Z-Score: `{z_score:.2f}`"
    send_telegram_alert(msg)
# إرسال رسالة تأكيد مع كل عملية فحص
status_msg = f"🔍 تم فحص السوق بنجاح\nالسعر: {close_price}\nZ-Score: {z_score:.2f}"
send_telegram_alert(status_msg)
