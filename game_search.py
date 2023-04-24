import requests
import config as cfg

"""Поиск сведений об игре """


def search_game_on_steam(app_id):
    about_game = {}

    response = requests.get('https://store.steampowered.com/api/appdetails',
                            params={'appids': app_id, 'cc': 'en', 'l': 'ru', 'format': 'json'})

    if response.status_code != 200:
        return 'not found'

    game_info = response.json()[str(app_id)]

    if game_info['success'] is False:
        return 'not found'

    game_info = game_info['data']
    about_game['header_image'] = game_info['header_image']  # иконка
    about_game['appid'] = game_info['steam_appid']  # id
    about_game['name'] = game_info['name']  # название
    about_game['genres'] = game_info.get('genres')  # жанры
    about_game['developers'] = game_info.get('developers')  # разработчики
    about_game["release_date"] = game_info['release_date']['date']  # дата реализации
    about_game['detailed_description'] = game_info['detailed_description']  # описание
    # цена
    if game_info['is_free']:
        about_game["price"] = 'free'
    else:
        try:
            about_game["price"] = game_info['price_overview']['final_formatted']
        except KeyError:
            about_game["price"] = "unknown :("

    # системные требования
    about_game['pc_requirements'] = {}
    if isinstance(game_info['pc_requirements'], list):
        if game_info['pc_requirements']:
            about_game['pc_requirements']['minimum'] = game_info['pc_requirements']
    else:
        if game_info['pc_requirements'].get('minimum'):
            about_game['pc_requirements']['minimum'] = game_info['pc_requirements']['minimum']
        if game_info['pc_requirements'].get('recommended'):
            about_game['pc_requirements']['recommended'] = game_info['pc_requirements']['recommended']

    about_game['mac_requirements'] = {}
    if isinstance(game_info['mac_requirements'], list):
        if game_info['mac_requirements']:
            about_game['mac_requirements']['minimum'] = game_info['mac_requirements']
    else:
        if game_info['mac_requirements'].get('minimum'):
            about_game['mac_requirements']['minimum'] = game_info['mac_requirements']['minimum']
        if game_info['mac_requirements'].get('recommended'):
            about_game['mac_requirements']['recommended'] = game_info['mac_requirements']['recommended']

    about_game['linux_requirements'] = {}
    if isinstance(game_info['linux_requirements'], list):
        if game_info['linux_requirements']:
            about_game['linux_requirements']['minimum'] = game_info['linux_requirements']
    else:
        if game_info['linux_requirements'].get('minimum'):
            about_game['linux_requirements']['minimum'] = game_info['linux_requirements']['minimum']
        if game_info['linux_requirements'].get('recommended'):
            about_game['linux_requirements']['recommended'] = game_info['linux_requirements']['recommended']

    if game_info.get('categories'):
        about_game['categories'] = game_info['categories']

    # видеоролики
    about_game['movies'] = []
    if game_info.get('movies'):
        for movie in game_info['movies']:
            if movie.get('mp4'):
                about_game['movies'].append(movie['mp4'][list(movie['mp4'])[-1]])
            elif movie.get('webm'):
                about_game['movies'].append(movie['webm'][list(movie['webm'])[-1]])

    about_game['background_raw'] = game_info['background_raw']

    # скриншоты
    if game_info.get('screenshots'):
        about_game['images'] = []
        for img in game_info['screenshots']:
            about_game['images'].append(img['path_full'])

    # количество игроков онлайн в данный момент
    try:
        url = f"https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
        params = {"key": cfg.API_KEY, "appid": app_id, "format": "json"}

        response = requests.get(url, params=params)
        data = response.json()

        about_game['player_count'] = data["response"]["player_count"]
    except Exception:
        about_game['player_count'] = None

    return about_game
