import os
import config
# from telebot import apihelper
import telebot

# apihelper.proxy = {'https': 'socks5://154.221.21.197:10800'}
bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello, I'm simple echo bot. Tell me something!")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)


if __name__ == '__main__':
    bot.polling()
