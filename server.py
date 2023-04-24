import validators
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, redirect, request, url_for, abort

from game_search import search_game_on_steam

from forms import RegisterForm, LoginForm, SearchUsersForm

from steam.steamid import SteamID

from data.users import User
from data import db_session

import re
import requests

from urllib import parse

import steamapi

import config as cfg


TITLE = 'Steamscroller'

# инициализируем приложение
app = Flask(__name__)
app.config['SECRET_KEY'] = cfg.FLASKAPP_SECRET_KEY

# инициализация системы авторизации
login_manager = LoginManager()
login_manager.init_app(app)

# инициализация базы данных
db_session.global_init("db/main.db")

# регулярные выражения для важных ссылок
steam_profile_re = re.compile(r'(?:https?://)?steamcommunity\.com/(?:profiles|id)/[a-zA-Z0-9]+(/?)\w')
steam_openid_re = re.compile(r'https://steamcommunity\.com/openid/id/(.*?)$')


@app.errorhandler(404)
def page_not_found(_):
    """Ошибка 404"""

    return render_template('404.html'), 404


@login_manager.user_loader
def load_user(user_id):
    """Подгрузка пользователя из базы данных"""

    return db_session.create_session().get(User, user_id)


@app.route('/logout/')
@login_required
def logout():
    """Выход из аккаунта"""

    logout_user()
    return redirect("/")


@app.route('/steamauth/')
def steam_auth():
    """Аутентификация через Steam (openid)"""

    # параметры для корректной работы аутентификации
    params = {
        'openid.ns': "http://specs.openid.net/auth/2.0",
        'openid.identity': "http://specs.openid.net/auth/2.0/identifier_select",
        'openid.claimed_id': "http://specs.openid.net/auth/2.0/identifier_select",
        'openid.mode': 'checkid_setup',
        'openid.return_to': request.url_root + url_for('login'),
        'openid.realm': request.url_root
    }

    param_string = parse.urlencode(params)
    auth_url = 'https://steamcommunity.com/openid/login?' + param_string
    # переход по ссылке в Steam, откуда потом мы вернёмся на наш сайт
    return redirect(auth_url)


@app.route('/searchuser/', methods=['GET', 'POST'])
def search_user():
    """Страница с формой для поиска пользователей Steam (по steamid или vanity url)"""

    if not current_user.is_authenticated:
        return redirect('/login')

    form = SearchUsersForm()
    if form.validate_on_submit():
        query = form.query.data
        # проверяем правильность данных

        if validators.url(query):
            # если это ссылка
            if not steam_profile_re.match(query):
                return render_template('forms/search_steam_user.html', title=f'{TITLE} :: Search Steam users',
                                       form=form,
                                       message="Incorrect format.<br>"
                                               "<br>"
                                               "Supported formats:<br>"
                                               "https://steamcommunity.com/id/mmger<br>"
                                               "https://steamcommunity.com/profiles/76561198037479071<br>"
                                               "mmger<br>"
                                               "76561198037479071")

            link_parts = steam_profile_re.match(query).group(0).split('/')
            query = link_parts[-1]

        if SteamID(query).is_valid():
            # если это steamid
            return redirect(url_for('steam_profile', steamid=int(query)))

        resolve_vanity = steamapi.api_caller.ISteamUser.ResolveVanityURL(vanityurl=query,
                                                                         url_type=1)['response']
        if resolve_vanity['success'] == 1:
            # если это vanity url
            return redirect(url_for('steam_profile', steamid=resolve_vanity['steamid']))
        if resolve_vanity['success'] == 42:
            return render_template('forms/search_steam_user.html', title=f'{TITLE} :: Search Steam users',
                                   form=form,
                                   message="Incorrect format.\n"
                                           "\n"
                                           "Supported formats:\n"
                                           "https://steamcommunity.com/id/mmger\n"
                                           "https://steamcommunity.com/profiles/76561198037479071\n"
                                           "mmger\n"
                                           "76561198037479071")
        return render_template('forms/search_steam_user.html', title=f'{TITLE} :: Search Steam users', form=form,
                               message=f"Failed to resolve Vanity URL, please try again."
                                       f" ({resolve_vanity['success']})")
    return render_template('forms/search_steam_user.html', title=f'{TITLE} :: Search Steam users', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    """Страница с формой для авторизации"""

    if request.args.get('openid.identity'):
        # если перешли с аутентификации через openid
        match = steam_openid_re.search(request.args['openid.identity'])
        if match:
            # если аутентификация прошла через Steam
            steamid = match.group(1)
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.steamid == str(steamid)).first()
            if user is None:
                # создаём пользователя если логинится впервые
                user_request = steamapi.api_caller.ISteamUser.GetPlayerSummaries(steamids=steamid)
                steam_user = user_request["response"]["players"][0]
                # noinspection PyArgumentList
                user = User(
                    steamid=steamid,
                    name=steam_user['personaname']
                )
                db_sess.add(user)
                db_sess.commit()
            login_user(user, remember=True)
            return redirect('/')

    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        # ищем, есть ли такой пользователь в базе данных
        user = db_sess.query(User).filter(User.email == str(form.email.data)).first()
        # noinspection PyArgumentList
        if user and user.check_password(form.password.data):
            # если пароль совпадает - всё хорошо
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('forms/login.html', title=f'{TITLE} :: Sign in', form=form,
                               message="Incorrect login or password")
    return render_template('forms/login.html', title=f'{TITLE} :: Sign in', form=form)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    """Страница с формой для регистрации"""

    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            # пароли не сходятся
            return render_template('forms/register.html', title='Регистрация', form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == str(form.email.data)).first():
            # пароли не сходятся
            return render_template('forms/register.html', title='Регистрация', form=form,
                                   message="There is already a user")
        # если всё хорошо - создаём нового пользователя
        # noinspection PyArgumentList
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data
        )
        # хэшируем пароль и добавляем пользователя в базу данных
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('forms/register.html', title=f"{TITLE} :: Sign up", form=form, flag=True)


@app.route("/")
def index():
    """Главная страница"""

    return render_template("index.html", title=TITLE)


@app.route("/profiles/<int:steamid>/cs2stats/")
@app.route("/profiles/<int:steamid>/csgostats/")
@app.route("/profiles/<int:steamid>/730stats/")
def steam_profile_730stats(steamid: int):
    """Страница со статистикой пользователя в CS:GO/CS2"""

    if not current_user.is_authenticated:
        return redirect('/login')

    user = steamapi.get_user(steamid)
    if not user:
        return 'User not found.'

    stats = steamapi.get_730_stats(steamid)

    return render_template('steam_profiles/730_stats.html', title=f"{TITLE} :: {user.nickname}",
                           user=user, stats=stats)


@app.route("/profiles/<int:steamid>/games/")
def steam_profile_games(steamid: int):
    """Страница с библиотекой пользователя"""

    if not current_user.is_authenticated:
        return redirect('/login')

    user = steamapi.get_user(steamid)
    if not user:
        return 'User not found.'

    games = steamapi.get_games(steamid)
    if games is not None:
        games = sorted(games, key=lambda x: (-x['playtime_forever'], x['appid']))

    return render_template('steam_profiles/games.html', title=f"{TITLE} :: {user.nickname}", user=user, games=games)


@app.route("/profiles/<int:steamid>/friends/")
def steam_profile_friends(steamid: int):
    """Страница со списком друзей пользователя"""

    if not current_user.is_authenticated:
        return redirect('/login')

    user = steamapi.get_user(steamid)
    if not user:
        return 'User not found.'

    friends = steamapi.get_friends(steamid)

    return render_template('steam_profiles/friends.html', title=f"{TITLE} :: {user.nickname}", user=user,
                           friends=friends)


@app.route("/profiles/<int:steamid>/")
def steam_profile(steamid: int):
    """Страница с профилем пользователя"""

    if not current_user.is_authenticated:
        return redirect('/login')

    user = steamapi.get_user(steamid)
    if not user:
        return 'User not found.'

    return render_template('steam_profiles/profile.html', title=f"{TITLE} :: {user.nickname}", user=user)


@app.route("/id/<string:vanityurl>/", strict_slashes=False)
def steam_profile_vanity(vanityurl: str):
    """Ссылка для поиска пользователя по vanity url через адресную строку"""

    if not current_user.is_authenticated:
        return redirect('/login')

    resolve_vanity = steamapi.api_caller.ISteamUser.ResolveVanityURL(vanityurl=vanityurl, url_type=1)['response']

    if resolve_vanity['success'] == 1:
        return redirect(url_for('steam_profile', steamid=resolve_vanity["steamid"]))

    if resolve_vanity['success'] == 42:
        return 'User not found.'

    # возможны сторонние ошибки
    return f'Error! Try again later. ({resolve_vanity["success"]})'


@app.route('/searchapp/<string:query>/')
def search_app(query: str):
    """Поиск приложения Steam по названию"""

    if not current_user.is_authenticated:
        return redirect('/login')

    return render_template('search/search_app.html', title=f'{TITLE} :: Searching "{query}"',
                           results=search_apps_by_name(query))


@app.route('/app/<int:appid>/')
def app_page(appid: int):
    """Страница приложения Steam"""

    if not current_user.is_authenticated:
        return redirect('/login')

    result = search_game_on_steam(appid)
    if result == 'not found':
        return abort(404)

    if result.get('developers'):
        result['developers'] = ', '.join(result['developers'])
    if result.get('genres'):
        result['genres'] = ', '.join(genre['description'] for genre in result['genres'])
    if result.get('categories'):
        result['categories'] = ', '.join(genre['description'] for genre in result['categories'])
    return render_template("steam_app.html", title=f'{TITLE} :: {result["name"]}', **result)


@app.route("/livesearch", methods=["POST", "GET"])
def livesearch():
    """"Живой поиск" - данная функция необходима для работы
       поисковой строки в шапке сайта
       ВАЖНО! Код поисковой строки написан на js внутри base.html"""

    query = request.form.get("query")
    if query is None:
        return redirect('/')

    results = search_apps_by_name(query)
    if len(results) > 10:
        results = results[:10]
        results.append('<see all>')
    return results


def search_apps_by_name(name: str):
    """Вспомогательная функция для поиска приложений Steam по названию
       Результаты сортируются по близости названия и appid"""

    requested_name = name.strip().lower()
    response = requests.get('http://api.steampowered.com/ISteamApps/GetAppList/v0002/',
                            params={'key': cfg.API_KEY, "type": "game"})
    if response.status_code != 200:
        return f'Error! Try again later. ({response.status_code})'

    apps = response.json()['applist']['apps']
    results = (_app for _app in apps if requested_name in _app['name'].strip().lower())
    results = sorted(results, key=lambda x: (x['name'].lower().index(requested_name), x['appid']))
    return results[:2000]


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
