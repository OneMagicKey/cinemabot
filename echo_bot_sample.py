import aiohttp
from bs4 import BeautifulSoup

import config
from telebot import types
import telebot

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def start_command(message: types.Message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Welcome to cinema bot!")


@bot.message_handler(func=lambda m: True)
async def find_movie(message: types.Message):
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
        links = await find_watch_online_film(movies[0]['title'], movies[0]['year'])
        watch_text = ''
        for link in links:
            watch_text += link + '\n'
        bot.send_message(user_id, watch_text)

    else:
        from kinopoisk.movie import Movie
        movie = Movie.objects.search(message.text)[0]
        if movie:
            movie.get_content('main_page')
            movie.get_content('posters')
            bot.send_message(user_id, movie.title + '\n' + movie.plot)
            bot.send_photo(user_id, movie.posters[0], movie.title)
            links = await find_watch_online_film(movie.title, movie.year)
            watch_text = ''
            for link in links:
                watch_text += link + '\n'
            bot.send_message(user_id, watch_text)
        else:
            bot.send_message(user_id, "Can't find " + message.text)


async def find_watch_online_film(title: str, year: str):
    rus_urls = [
        'https://www.ivi.ru',
        'https://okko.tv',
        'https://www.tvzavr.ru',
    ]
    trunc_rus_urls = ['.'.join(url.split('.')[:-1]) for url in rus_urls]
    google = 'https://www.google.ru/search'
    header = {
        'user-agent': (
            'Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.1.8) Gecko/20100214 Linux Mint/8 (Helena) Firefox/'
                      '3.5.8'
        )
    }
    movies_links = []
    async with aiohttp.ClientSession() as session:
        for url, trunc_url in zip(rus_urls, trunc_rus_urls):
            params = {
                'q': 'site:' + url + ' ' + title + ' ' + year + ' смотреть',
            }
            async with session.get(google, params=params, headers=header) as resp:
                search_rsp = await resp.text()
                soup = BeautifulSoup(search_rsp, 'lxml')
                for link in soup.find_all('a'):
                    if link.get('href') and link.get('href').startswith(trunc_url):
                        movies_links.append(link.get('href'))
                        break
    return movies_links


if __name__ == '__main__':
    bot.polling(none_stop=True, timeout=300)
