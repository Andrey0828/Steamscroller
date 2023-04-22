import requests


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
    about_game['header_image'] = game_info['header_image']
    about_game['appid'] = game_info['steam_appid']
    about_game['name'] = game_info['name']
    about_game['genres'] = game_info['genres']
    about_game['developers'] = game_info['developers']
    about_game["release_date"] = game_info['release_date']['date']
    about_game['detailed_description'] = game_info['detailed_description']
    if game_info['is_free']:
        about_game["price"] = 'free'
    else:
        try:
            about_game["price"] = game_info['price_overview']['final_formatted']
        except KeyError:
            about_game["price"] = "unknown :("

    about_game['pc_requirements'] = {}
    if isinstance(game_info['pc_requirements'], list):
        about_game['pc_requirements']['minimum'] = game_info['pc_requirements']
    else:
        if game_info['pc_requirements'].get('minimum'):
            about_game['pc_requirements']['minimum'] = game_info['pc_requirements']['minimum']
        if game_info['pc_requirements'].get('recommended'):
            about_game['pc_requirements']['recommended'] = game_info['pc_requirements']['recommended']

    about_game['mac_requirements'] = {}
    if isinstance(game_info['mac_requirements'], list):
        about_game['mac_requirements']['minimum'] = game_info['mac_requirements']
    else:
        if game_info['mac_requirements'].get('minimum'):
            about_game['mac_requirements']['minimum'] = game_info['mac_requirements']['minimum']
        if game_info['mac_requirements'].get('recommended'):
            about_game['mac_requirements']['recommended'] = game_info['mac_requirements']['recommended']

    about_game['linux_requirements'] = {}
    if isinstance(game_info['linux_requirements'], list):
        about_game['linux_requirements']['minimum'] = game_info['linux_requirements']
    else:
        if game_info['linux_requirements'].get('minimum'):
            about_game['linux_requirements']['minimum'] = game_info['linux_requirements']['minimum']
        if game_info['linux_requirements'].get('recommended'):
            about_game['linux_requirements']['recommended'] = game_info['linux_requirements']['recommended']

    if game_info.get('categories'):
        about_game['categories'] = game_info['categories']

    about_game['movies'] = []
    if game_info.get('movies'):
        for movie in game_info['movies']:
            if movie.get('mp4'):
                about_game['movies'].append(movie['mp4'][list(movie['mp4'])[-1]])
            elif movie.get('webm'):
                about_game['movies'].append(movie['webm'][list(movie['webm'])[-1]])

    about_game['background_raw'] = game_info['background_raw']
    if game_info.get('screenshots'):
        about_game['images'] = []
        for img in game_info['screenshots']:
            about_game['images'].append(img['path_full'])

    return about_game
