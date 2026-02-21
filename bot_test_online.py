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

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=scopes
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # ===== 1️ Hello =====
    if text.lower() == "hello":
        await update.message.reply_text("Xin chào, tôi có thể giúp gì cho bạn?")
        return

    # ===== 2 Bye =====
    if text.lower() == "bye":
        await update.message.reply_text("Chúc bạn ngày mới tốt lành")
        return

    # =====================================================
    # ===== 3 CẬP NHẬT TIẾN ĐỘ ST.[MaSite].[A/B/C]
    # =====================================================

    if text.startswith("ST."):
        parts = text.split(".")

        if len(parts) != 3:
            await update.message.reply_text(
                "Sai cú pháp!\nVui lòng nhập:\nST.[MãSite].[A/B/C]"
            )
            return

        site_code = parts[1].strip()
        status_code = parts[2].strip().upper()

        status_map = {
            "A": "Chưa thực hiện",
            "B": "Đang thực hiện",
            "C": "Hoàn thành"
        }

        if status_code not in status_map:
            await update.message.reply_text(
                "Giá trị tiến độ không hợp lệ!\nChỉ dùng A, B hoặc C."
            )
            return

        status_text = status_map[status_code]

        data = sheet.get_all_values()

        for index, row in enumerate(data):
            if len(row) >= 1 and row[0].strip().lower() == site_code.lower():

                # Cập nhật cột D (cột thứ 4)
                sheet.update_cell(index + 1, 4, status_text)

                await update.message.reply_text(
                    f"Đã cập nhật tiến độ cho {site_code}:\n{status_text}"
                )
                return

        await update.message.reply_text("Không tìm thấy Mã Site.")
        return

    # =====================================================
    # ===== 4 TRA CỨU TC.[TênSite]
    # =====================================================

    if text.startswith("TC."):

        site_name = text[3:].strip()

        data = sheet.get_all_values()

        for row in data:
            if len(row) >= 3 and row[0].strip().lower() == site_name.lower():
                xa = row[1]
                dia_chi = row[2]

                table = (
                "+------------+------------------+\n"
                f"| 📍Xã         | {xa:<22} |\n"
                "+------------+------------------+\n"
                f"| 🏠Địa chỉ    | {dia_chi:<22} |\n"
                "+------------+------------------+"
                )

                await update.message.reply_text(
                    f"Kết quả tra cứu của mã nhà trạm {site_name} là: \n <pre>{table}</pre>",parse_mode="HTML"
                )
                return

        await update.message.reply_text("Không tìm thấy dữ liệu.")
        return

    # ===== 5 Sai cú pháp =====
    await update.message.reply_text(
        "Sai cú pháp!\n\n"
        "Tra cứu: TC.[TênSite]\n"
        "Cập nhật tiến độ: ST.[MãSite].[A/B/C]"
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

PORT = int(os.environ.get("PORT", 10000))

app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=f"https://vietnh17-test-chatbot.onrender.com/{TOKEN}",
    url_path=TOKEN
)