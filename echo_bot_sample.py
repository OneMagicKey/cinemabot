import asyncio
import aiohttp
from bs4 import BeautifulSoup

import config
from telebot import types
import telebot

bot = telebot.TeleBot(config.token)
users = []
usr_language = {}


@bot.message_handler(commands=['start'])
def start_command(message: types.Message):
    user_id = message.from_user.id
    users.append(user_id)
    usr_language[user_id] = 'en'
    bot.send_message(user_id, 'Welcome to the cinema bot!')
    if usr_language[user_id] == 'ru':
        text = (
            'Выберите язык \n\n'
            'Поиск фильмов осуществляется на выбранном языке'
        )
        bot.send_message(user_id, text, parse_mode='markdown', reply_markup=types.InlineKeyboardMarkup().
                         row(types.InlineKeyboardButton('Русский', callback_data='language_ru'),
                             types.InlineKeyboardButton('English', callback_data='language_en')))
    else:
        text = (
            'Select your language \n\n'
            'Films will be searched in chosen language'
        )
        bot.send_message(user_id, text, parse_mode='markdown', reply_markup=types.InlineKeyboardMarkup().
                         row(types.InlineKeyboardButton('Русский', callback_data='language_ru'),
                             types.InlineKeyboardButton('English', callback_data='language_en')))


@bot.message_handler(commands=['help'])
def help_command(message: types.Message):
    user_id = message.from_user.id
    if usr_language.get(user_id, 'en') == 'en':
        text = (
            'Please use /start command to start the bot and choose the language \n'
            'You can use /settings command to change language \n'
            'After that you may start using the bot and find movies \n'
            'Query examples: \n'
            'Venom \n'
            'Avengers Endgame \n'
            'Rick and Morty'
        )
        bot.send_message(user_id, text, parse_mode='markdown')
    else:
        text = (
            'Используйте команду /start для старта бота и выберете язык \n'
            'Команда /settings позволяет сменить язык бота \n'
            'После этого можно попросить бота найти фильм \n'
            'Примеры запросов к боту: \n'
            'Веном \n'
            'Мстители Финал \n'
            'Рик и Морти'
        )
        bot.send_message(user_id, text, parse_mode='markdown')


@bot.message_handler(commands=['settings'])
def help_command(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        text = (
            'You should /start the bot and choose the language'
        )
        bot.send_message(user_id, text)
    else:
        if usr_language[user_id] == 'ru':
            text = (
                'Выберите язык \n\n'
                'Поиск фильмов осуществляется на выбранном языке'
            )
            bot.send_message(user_id, text, parse_mode='markdown', reply_markup=types.InlineKeyboardMarkup().
                             row(types.InlineKeyboardButton('Русский', callback_data='language_ru'),
                                 types.InlineKeyboardButton('English', callback_data='language_en')))
        else:
            text = (
                'Select your language \n\n'
                'Films will be searched in chosen language'
            )
            bot.send_message(user_id, text, parse_mode='markdown', reply_markup=types.InlineKeyboardMarkup().
                             row(types.InlineKeyboardButton('Русский', callback_data='language_ru'),
                                 types.InlineKeyboardButton('English', callback_data='language_en')))


@bot.message_handler(func=lambda m: True)
def find_movie(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        text = (
            'You should /start the bot and choose the language'
        )
        bot.send_message(user_id, text)
    else:
        if usr_language[user_id] == 'ru':
            find_movie_in_ru(message, user_id)
        else:
            find_movie_in_en(message, user_id)


def find_movie_in_ru(message: types.Message, user_id: str):
    from kinopoisk.movie import Movie
    movie = Movie.objects.search(message.text)
    if movie:
        movie = movie[0]
        setattr(movie, 'career', {})
        movie.get_content('main_page')
        movie.get_content('cast')
        bot.send_message(user_id, movie.title + '\n' + movie.plot)
        try:
            movie.get_content('posters')
            bot.send_photo(user_id, movie.posters[0])
        except ValueError:
            pass
        # loop = asyncio.new_event_loop()
        links = find_watch_online_ru(movie.title, movie.year)
        refs = ''
        for link in links:
            refs += link + '\n'
        bot.send_message(user_id, refs)
    else:
        bot.send_message(user_id, "Не могу найти " + message.text)


def find_movie_in_en(message: types.Message, user_id: str):
    from imdb import IMDb
    ia = IMDb()
    found_movies = ia.search_movie(title=message.text, results=3)
    movies = []
    for movie in found_movies:
        ia.update(movie, info=['plot', 'vote details'])
        if movie.get('number of votes') is not None and movie.get('plot') is not None:
            movies.append(movie)
    if movies:
        movies.sort(key=lambda mov: sum(mov.get('number of votes').values()), reverse=True)
        bot.send_message(user_id, str(movies[0]['title']) + '\n' + movies[0]['plot'][0])
        try:
            bot.send_photo(user_id, movies[0]['full-size cover url'])
        except telebot.apihelper.ApiException:
            pass
        # loop = asyncio.new_event_loop()
        links = find_watch_online_en(movies[0]['title'], movies[0]['year'])
        refs = ''
        for link in links:
            refs += link + '\n'
        bot.send_message(user_id, refs)
    else:
        bot.send_message(user_id, "Can't find " + message.text)


def find_watch_online_ru(title: str, year: str):
    urls = [
        'https://www.ivi.ru',
        'http://kinodron.net/',
        'https://tv.filmshd.fun/',
        'https://okko.tv',
        'https://onlinemultfilmy.ru/',
        'https://www.tvzavr.ru',
        'https://megogo.ru/'
    ]
    text = 'смотреть онлайн'
    return asyncio.new_event_loop().run_until_complete(find_watch_online_film(urls, title, year, text))


def find_watch_online_en(title: str, year: str):
    urls = [
        'https://www.amazon.com',
        'https://www.netflix.com',
        'https://itunes.apple.com/'
    ]
    text = 'watch online'
    return asyncio.new_event_loop().run_until_complete(find_watch_online_film(urls, title, year, text))


async def find_watch_online_film(urls, title: str, year: str, text):
    trunc_urls = ['.'.join(url.split('.')[:-1]) for url in urls]
    google = 'https://www.google.com/search?'
    header = {
        'user-agent': (
            'Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.1.8) Gecko/20100214 Linux Mint/8 (Helena) Firefox/'
                      '3.5.8'
        )
    }
    movies_links = []
    async with aiohttp.ClientSession() as session:
        for url, trunc_url in zip(urls, trunc_urls):
            params = {
                'q': 'site:' + url + ' ' + title + ' ' + str(year) + ' ' + text,
            }
            async with session.get(google, params=params, headers=header) as resp:
                search_rsp = await resp.text()
                soup = BeautifulSoup(search_rsp, 'lxml')
                for link in soup.find_all('a'):
                    if link.get('href')[7:] and link.get('href')[7:].startswith(trunc_url):
                        movies_links.append(link.get('href')[7:].split('&')[0])
                        break
    return movies_links


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery):
    data = call.data.split('_')
    user_id = call.from_user.id
    if data[1] == 'ru':
        usr_language[user_id] = 'ru'
    else:
        usr_language[user_id] = 'en'


if __name__ == '__main__':
    bot.polling(none_stop=True, timeout=300)
