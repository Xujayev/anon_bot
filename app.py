import os
from flask import Flask, request
import telebot

TOKEN = os.environ.get("BOT_TOKEN")  # Render Environment Variable
bot = telebot.TeleBot(TOKEN)

ADMINS = [8129357130]  # Admin ID lar
messages_map = {}  # user_id -> list of sent message_ids

app = Flask(__name__)

# Webhook endpoint
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    text = message.text.split()
    if len(text) > 1:
        receiver_id = text[1]
        if str(user_id) == receiver_id:
            bot.send_message(user_id, "O'zingizga anonim xabar yubora olmaysiz! 😊")
            return
        msg = bot.send_message(user_id, "Anonim savolingizni yuboring:")
        bot.register_next_step_handler(msg, send_anonymous_message, receiver_id)
    else:
        if user_id in ADMINS:
            my_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
            bot.send_message(user_id, f"Salom Admin! Sizning anonim havolangiz:\n\n{my_link}")
        else:
            bot.send_message(user_id, "Xabar yuborish uchun sizga berilgan maxsus havolani bosing.")

# Cheksiz xabar yuborish
def send_anonymous_message(message, receiver_id):
    if not message.text:
        bot.send_message(message.chat.id, "Iltimos, faqat matnli xabar yuboring.")
        return

    try:
        sent_msg = bot.send_message(receiver_id, f"📩 Yangi anonim xabar:\n\n{message.text}")

        # Foydalanuvchi ID bo'yicha saqlash
        if message.chat.id in messages_map:
            messages_map[message.chat.id].append(sent_msg.message_id)
        else:
            messages_map[message.chat.id] = [sent_msg.message_id]

        bot.send_message(message.chat.id, "Xabaringiz yuborildi! ✅")
    except Exception as e:
        bot.send_message(message.chat.id, "Xatolik yuz berdi.")

# Javob berish
@bot.message_handler(func=lambda message: message.reply_to_message is not None)
def reply_to_anon(message):
    if message.chat.id not in ADMINS:
        return

    original_msg_id = message.reply_to_message.message_id

    for user_id, msg_ids in messages_map.items():
        if original_msg_id in msg_ids:
            try:
                bot.send_message(user_id, f"Sizning savolingizga javob keldi:\n\n{message.text}")
                bot.send_message(message.chat.id, "Javob yuborildi! 📤")
            except:
                bot.send_message(message.chat.id, "Foydalanuvchiga yuborib bo'lmadi.")
            break

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://YOUR_RENDER_APP.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
