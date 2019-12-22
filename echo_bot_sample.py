import config
from telebot import types
# from telebot import apihelper
import telebot

# apihelper.proxy = {'https': 'socks5://154.221.21.197:10800'}
bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def start_command(message: types.Message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Welcome to cinema bot")


@bot.message_handler(func=lambda m: True)
def find_movie(message: types.Message):
    from imdb import IMDb
    ia = IMDb()
    user_id = message.from_user.id
    movie = ia.search_movie(title=message.text)
    if movie:
        bot.send_message(user_id, movie[0].get_current_info())
    else:
        bot.send_message(user_id, "Can't find" + message.text)


if __name__ == '__main__':
    bot.polling()
