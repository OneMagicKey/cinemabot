import config
from telebot import types
import telebot
# from telebot import apihelper
# apihelper.proxy = {'https': 'socks5h://54.39.16.26:41279'}
bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def start_command(message: types.Message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Welcome to cinema bot!")


@bot.message_handler(func=lambda m: True)
def find_movie(message: types.Message):
    from imdb import IMDb
    ia = IMDb()
    user_id = message.from_user.id
    found_movies = ia.search_movie(title=message.text, results=3)
    movies = []
    for movie in found_movies:
        ia.update(movie, info=['plot', 'vote details'])
        if movie.get('number of votes') is not None:
            movies.append(movie)

    if movies:
        movies.sort(key=lambda mov: sum(mov.get('number of votes').values()), reverse=True)
        bot.send_message(user_id, movies[0].summary())
        bot.send_photo(user_id, movies[0]['full-size cover url'], movies[0]['title'])
    else:
        from kinopoisk.movie import Movie
        movie = Movie.objects.search(message.text)[0]
        if movie:
            movie.get_content('main_page')
            bot.send_message(user_id, movie.title)
            bot.send_photo(user_id, movie.get_content('posters'), movie.title)
        else:
            bot.send_message(user_id, "Can't find " + message.text)


if __name__ == '__main__':
    bot.polling(none_stop=True, timeout=300)
