import asyncio
import aiohttp
from bs4 import BeautifulSoup
import config
from imdb import IMDb
from kinopoisk.movie import Movie
from telebot import types
import telebot

bot = telebot.TeleBot(config.token)
users = []
usr_language = {}


@bot.message_handler(commands=['start'])
def start_command(message: types.Message):
    """ Function to handle the start command and request bot language

    :param message: message with user_id
    """
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
            'Films will be searched in selected language'
        )
        bot.send_message(user_id, text, parse_mode='markdown', reply_markup=types.InlineKeyboardMarkup().
                         row(types.InlineKeyboardButton('Русский', callback_data='language_ru'),
                             types.InlineKeyboardButton('English', callback_data='language_en')))


@bot.message_handler(commands=['help'])
def help_command(message: types.Message):
    """ Function to handle the help command. Prints a list of available bot commands.

    :param message: message with user_id
    """
    user_id = message.from_user.id
    if usr_language.get(user_id, 'en') == 'en':
        text = (
            'Please use /start command to start the bot and select the language \n'
            'You can use /settings command to change language \n'
            'After that you may start using the bot and find movies \n'
            'Query examples: \n'
            'Venom \n'
            'Avengers Endgame \n'
            'Rick and Morty'
        )
        bot.send_message(user_id, text)
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
        bot.send_message(user_id, text)


@bot.message_handler(commands=['settings'])
def setting_command(message: types.Message):
    """ Function to handle the settings command and changing the bot language

    :param message: message with user_id
    """
    user_id = message.from_user.id
    if user_id not in users:
        text = (
            'You should /start the bot and select the language'
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
    """ Finding movies based on user language

    :param message: message with user_id and movie title
    """
    user_id = message.from_user.id
    if user_id not in users:
        text = (
            'You should /start the bot and choose the language'
        )
        bot.send_message(user_id, text)
    else:
        if usr_language[user_id] == 'ru':
            asyncio.run(find_movie_in_ru(message, user_id))
        else:
            asyncio.run(find_movie_in_en(message, user_id))


async def find_movie_in_ru(message: types.Message, user_id: str):
    """ Finding movies on russian language and send movie poster and title to user

    :param message: message movie title
    :param user_id: user_id for send message to
    """
    movies = Movie.objects.search(message.text)
    mov = []
    for movie in movies[:3]:
        if movie.votes is not None:
            mov.append(movie)
    if mov:
        movie = mov[0]
        setattr(movie, 'career', {})
        try:
            movie.get_content('main_page')
        except IndexError:
            pass
        nl = '\n'
        bot.send_message(user_id, f'*{movie.title}*{nl}{movie.plot}', parse_mode='markdown')
        photo = f'https://st.kp.yandex.net/images/film_big/{movie.id}.jpg'
        bot.send_photo(user_id, photo)
        links = await find_watch_online_ru(movie.title, movie.year)
        refs = f"Ссылки: {nl}{nl.join(links)}"
        bot.send_message(user_id, refs)
    else:
        bot.send_message(user_id, f'Не могу найти {message.text}')


async def find_movie_in_en(message: types.Message, user_id: str):
    """ Finding movies on english language and send movie poster and title to user

    :param message: message movie title
    :param user_id: user_id for send message to
    """
    ia = IMDb()
    found_movies = ia.search_movie(title=message.text, results=3)
    movies = []
    for movie in found_movies:
        ia.update(movie, info=['plot', 'vote details'])
        if movie.get('number of votes') is not None and movie.get('plot') is not None:
            movies.append(movie)
    if movies:
        movies.sort(key=lambda mov: sum(mov.get('number of votes').values()), reverse=True)

        title = f"*{movies[0]['title']}*"
        plot = movies[0]['plot'][0].split('::')[0]
        nl = '\n'
        bot.send_message(user_id,  f'{title}{nl}{plot}', parse_mode='markdown')
        try:
            bot.send_photo(user_id, movies[0]['full-size cover url'])
        except telebot.apihelper.ApiException:
            pass
        links = await find_watch_online_en(movies[0]['title'], movies[0]['year'])
        refs = f"Links: {nl}{nl.join(links)}"
        bot.send_message(user_id, refs)
    else:
        bot.send_message(user_id, f"Can't find {message.text}")


async def find_watch_online_ru(title: str, year: str):
    urls = [
        'https://www.film.ru',
        'https://www.ivi.ru',
        'http://kinodron.net',
        'https://tv.filmshd.fun',
        'https://okko.tv',
        'https://onlinemultfilmy.ru',
        'http://serialogo.ucoz.net',
        'https://www.tvzavr.ru',
        'https://megogo.ru',
    ]
    text = 'смотреть'
    return await find_watch_online_film(urls, title, year, text)


async def find_watch_online_en(title: str, year: str):
    urls = [
        'https://www.amazon.com',
        'https://www.netflix.com',
        'https://itunes.apple.com',
    ]
    text = 'watch'
    return await find_watch_online_film(urls, title, year, text)


async def find_watch_online_film(urls: list, title: str, year: str, text: str):
    """ Finding links to watch film online

    :param urls: list of sites for finding movies
    :param title: title of the movie
    :param year: year of the movie release
    """
    start_urls = ['.'.join(url.split('.')[:-1]) for url in urls]
    header = {
        'user-agent': (
            'Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.1.8) Gecko/20100214 Linux Mint/8 (Helena) Firefox/'
            '3.5.8'
        )
    }
    movies_refs = []
    async with aiohttp.ClientSession() as session:
        for url, start_url in zip(urls, start_urls):
            param = {
                f'q: site:{url} {title} {year} {text}'
                # 'q': 'site:' + url + ' ' + title + ' ' + str(year) + ' ' + text,
            }
            async with session.get('https://www.google.com/search?', params=param, headers=header) as resp:
                soup = BeautifulSoup(await resp.text(), 'lxml')
                for link in soup.find_all('a'):
                    if link.get('href') and link.get('href').startswith(start_url):
                        movies_refs.append(link.get('href').split('&')[0])
                        break
    return movies_refs


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery):
    """ Callback function to handle the buttons"""
    data = call.data.split('_')
    user_id = call.from_user.id
    if data[1] == 'ru':
        usr_language[user_id] = 'ru'
        bot.send_message(user_id, "Язык сохранён!")
    else:
        usr_language[user_id] = 'en'
        bot.send_message(user_id, "Language has been saved!")


if __name__ == '__main__':
    bot.polling(none_stop=True, timeout=300)
