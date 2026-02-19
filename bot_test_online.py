import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import gspread
from google.oauth2.service_account import Credentials
import json

# ===== TELEGRAM TOKEN =====
TOKEN = os.environ.get("TOKEN")

# ===== GOOGLE SHEET =====
SHEET_ID = os.environ.get("SHEET_ID")

# ===== SERVICE ACCOUNT JSON từ ENV =====
service_account_info = json.loads(os.environ.get("GOOGLE_CREDENTIALS"))

scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=scopes
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    data = sheet.get_all_values()

    for row in data:
        if len(row) >= 3 and row[0].strip() == text:
            xa = row[1]
            dia_chi = row[2]
            await update.message.reply_text(f"Xã: {xa}\nĐịa chỉ: {dia_chi}")
            return

    await update.message.reply_text("Không tìm thấy dữ liệu.")


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

PORT = int(os.environ.get("PORT", 10000))

app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=f"https://vietnh17-test-chatbot.onrender.com/{TOKEN}"
)