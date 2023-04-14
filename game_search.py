import difflib

import requests
from bs4 import BeautifulSoup
from sys import platform


def search_game_on_steam(game_name):
    about_game = {}
    os = None

    api_url = f"https://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMAPIKEY&format=json"
    response = requests.get(api_url)

    if response.status_code != 200:
        return response.status_code

    app_list = response.json()['applist']['apps']
    s = [app["name"].lower() for app in app_list]
    dif = difflib.get_close_matches(game_name.lower(), s)
    if dif[0] is not None:
        app_id = None
        for app in app_list:
            if app['name'].lower() == game_name.lower():
                app_id = app['appid']
                break
        if app_id is not None:
            app_details_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc=ru&l=ru&format=json"
            response = requests.get(app_details_url)

            if response.status_code != 200:
                return response.status_code

            game_info = response.json()[str(app_id)]

        else:
            return "Игра не найдена"

        if game_info["success"]:
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
                os = "window"
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
        else:
            return "Данный товар недоступен в вашем регионе"
    else:
        return "Игра не найдена"
