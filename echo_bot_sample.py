import os
import telebot


bot = telebot.TeleBot(os.environ['1043723909:AAGsTVTyMS6lBwvZ2MUoxSKpCidb6XWeLSU'])


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello, I'm simple echo bot. Tell me something!")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)


if __name__ == '__main__':
    bot.polling()
