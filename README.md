# Cinema Bot
Бот [@watch_cinema_online_bot](https://t.me/watch_cinema_online_bot)

# Поиск фильмов

Для поиска фильмов используются библиотеки **kinopoiskpy**(для фильмов на русском) и **imdbpy**(для фильмов на английском).
Список фильмов, полученных после запроса, сортируется по убывания **количества оценок**. После этого выбирается фильм (или сериал) 
с наибольшим числом оценок и начинается поиск ссылок на соответствующих сайтах(в зависимости от выбора языка) для онлайн просмотра этого фильма.

# Список команд

- */start* -- запускает бота и позволяет вырбрать язык поиска
- */help*  -- выводит список доступных команд и примеры запросов к боту
- */settings* -- позволяет сменить язык бота

#Сервер

Бот задеплоин на [heroku](https://cinemabot666.herokuapp.com/)