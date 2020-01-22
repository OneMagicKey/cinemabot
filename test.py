import bot
from imdb import IMDb
from kinopoisk.movie import Movie


def find_movie_en(text: str):
    ia = IMDb()
    found_movies = ia.search_movie(title=text, results=3)
    movies = []
    for movie in found_movies:
        ia.update(movie, info=['plot', 'vote details'])
        if movie.get('number of votes') is not None and movie.get('plot') is not None:
            movies.append(movie)
    movies.sort(key=lambda mov: sum(mov.get('number of votes').values()), reverse=True)
    title = movies[0]['title']
    plot = movies[0]['plot'][0].split('::')[0]
    poster = movies[0]['full-size cover url']
    return title, plot, poster


def find_movie_ru(text: str):
    movies = Movie.objects.search(text)
    mov = []
    for movie in movies[:3]:
        if movie.votes is not None:
            mov.append(movie)
    movie = mov[0]
    setattr(movie, 'career', {})
    try:
        movie.get_content('main_page')
    except IndexError:
        pass
    photo = f'https://st.kp.yandex.net/images/film_big/{movie.id}.jpg'
    return movie.title, movie.plot, photo


def test_search_en_movie():
    titles = ['Inception', 'Avatar', 'Game of Thrones', 'God Father']
    for title in titles:
        tit, plot, poster = find_movie_en(title)
        assert tit
        assert plot
        assert poster


def test_search_ru_movie():
    titles = ['Мстители: Финал', 'Веном', 'Разачоравание', 'Холоп', 'Притяжение']
    for title in titles:
        tit, plot, poster = find_movie_ru(title)
        assert tit
        assert plot
        assert poster


def test_search_ru_links():
    info = [('Мстители: Финал', 2019), ('Веном', 2018), ('Рик и Морти', 2013)]
    for title, year in info:
        links = bot.find_watch_online_ru(title, str(year))
        assert links


def test_search_en_links():
    info = [('Inception', 2010), ('Naruto', 2002), ('Game of Thrones', 2011)]
    for title, year in info:
        links = bot.find_watch_online_en(title, str(year))
        assert links

