import difflib

import requests
from bs4 import BeautifulSoup
from sys import platform


def search_game_on_steam(app_id):
    about_game = {}
    os = None

    response = requests.get('https://store.steampowered.com/api/appdetails',
                            params={'appids': app_id, 'cc': 'en', 'l': 'ru', 'format': 'json'})

    if response.status_code != 200:
        return 'Игра не найдена'

    game_info = response.json()[str(app_id)]

    if not game_info["success"]:
        return 'Данный товар недоступен в вашем регионе'

    game_info = game_info['data']
    about_game["avatar_of_the_game"] = game_info['header_image']
    about_game["name"] = game_info['name']
    about_game["genres"] = ', '.join([genre['description'] for genre in game_info['genres']])
    about_game["developer"] = ', '.join(game_info['developers'])
    about_game["release_date"] = game_info['release_date']['date']
    about_game["description_of_the_game"] = BeautifulSoup(game_info['detailed_description'], 'lxml').get_text()
    try:
        about_game["price"] = game_info['price_overview']['final_formatted']
    except KeyError:
        about_game["price"] = "бесплатно"
    if platform == "linux" or platform == "linux2":
        os = "linux"
        try:
            par = BeautifulSoup(game_info['linux_requirements']['recommended'], 'lxml').get_text()
            about_game["recommended_system_requirements"] = par[par.find(':') + 1:]
        except KeyError:
            par = BeautifulSoup(game_info['linux_requirements']['minimum'], 'lxml').get_text()
            about_game["minimum_system_requirements"] = par[par.find(':') + 1:]
    elif platform == "darwin":
        os = "mac"
        try:
            par = BeautifulSoup(game_info['mac_requirements']['recommended'], 'lxml').get_text()
            about_game["recommended_system_requirements"] = par[par.find(':') + 1:]
        except KeyError:
            par = BeautifulSoup(game_info['mac_requirements']['minimum'], 'lxml').get_text()
            about_game["minimum_system_requirements"] = par[par.find(':') + 1:]
    elif platform == "win32" or platform == "win64":
        os = "windows"
        try:
            par = BeautifulSoup(game_info['pc_requirements']['recommended'], 'lxml').get_text()
            about_game["recommended_system_requirements"] = par[par.find(':') + 1:]
        except KeyError:
            par = BeautifulSoup(game_info['pc_requirements']['minimum'], 'lxml').get_text()
            about_game["minimum_system_requirements"] = par[par.find(':') + 1:]
    if game_info['categories'][0].get('description') is not None:
        about_game["mode"] = game_info['categories'][0]['description']
    try:
        if game_info['movies'][0]['mp4'].get('max') is not None:
            about_game["video"] = game_info['movies'][0]['mp4']['max']
    except KeyError:
        pass
    about_game["background"] = game_info['background_raw']
    about_game["images"] = []
    for i in game_info["screenshots"]:
        about_game["images"].append(i["path_full"])
    return about_game, os

