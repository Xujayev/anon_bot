import os
from flask import Flask, request
import telebot

TOKEN = os.environ.get("8455320633:AAFQOMv2DYj3HkLuvcuvuD1zfrustzeb5Ik") 
bot = telebot.TeleBot(TOKEN)

ADMINS = [8129357130]
messages_map = {}

app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

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

def send_anonymous_message(message, receiver_id):
    if not message.text:
        bot.send_message(message.chat.id, "Iltimos, faqat matnli xabar yuboring.")
        return
    try:
        sent_msg = bot.send_message(receiver_id, f"📩 Yangi anonim xabar:\n\n{message.text}")
        messages_map[sent_msg.message_id] = message.chat.id
        bot.send_message(message.chat.id, "Xabaringiz yuborildi! ✅")
    except Exception as e:
        bot.send_message(message.chat.id, "Xatolik yuz berdi.")

@bot.message_handler(func=lambda message: message.reply_to_message is not None)
def reply_to_anon(message):
    if message.chat.id not in ADMINS:
        return
    original_msg_id = message.reply_to_message.message_id
    if original_msg_id in messages_map:
        sender_user_id = messages_map[original_msg_id]
        try:
            bot.send_message(sender_user_id, f"Sizning savolingizga javob keldi:\n\n{message.text}")
            bot.send_message(message.chat.id, "Javob yuborildi! 📤")
        except:
            bot.send_message(message.chat.id, "Foydalanuvchiga yuborib bo'lmadi.")
    else:
        bot.send_message(message.chat.id, "Xabarni topa olmadim.")

if __name__ == "__main__":
    # Render uchun webhook set
    bot.remove_webhook()
    bot.set_webhook(url=f"https://YOUR_RENDER_APP.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
