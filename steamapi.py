from typing import NamedTuple
import datetime as dt

import requests
from steam.steamid import SteamID
from steam.webapi import WebAPI

import config as cfg
from games import Appid730GameStats
from country_name import search_country_by_name


# объект, который обращается к Steam WebAPI
api_caller = WebAPI(key=cfg.STEAM_API_KEY)


class SteamUser(NamedTuple):
    """Контейнер для хранения информации о пользователе Steam"""

    class Bans(NamedTuple):
        """Контейнер для хранения информации о блокировках пользователя"""

        community_ban: bool
        vac_bans: int
        game_bans: int
        economy_ban: bool
        days_since_last_ban: int

    id: int
    nickname: str
    name: str
    avatar: str
    level: int
    country: str
    profile_created: str
    last_logoff: str
    bans: Bans


class SteamUserFriend(NamedTuple):
    """Контейнер для хранения информации о друге пользователя"""

    id: int
    nickname: str
    avatar: str


def get_user(steamid: int):
    """Получаем контейнер SteamUser по steamid пользователя"""

    if not SteamID(steamid).is_valid():
        return

    # собираем основную информацию о пользователе
    player_request = api_caller.ISteamUser.GetPlayerSummaries(steamids=steamid)["response"]["players"]
    if not player_request:
        return

    user = player_request[0]
    # если пользователь скрыл профиль и часть данных - мы не получим их
    # например, уровень
    level = api_caller.IPlayerService.GetSteamLevel(steamid=steamid)['response'].get('player_level')

    nick = user['personaname']  # никнейм
    name = user.get('realname')  # имя
    avatar = user.get('avatarfull')  # аватар
    country = user.get('loccountrycode')  # код страны
    if country:
        country = search_country_by_name(country)
        # возможно этой страны нет в нашем списке
        if country:
            country = country.name
    profile_created = user.get('timecreated')  # время создания профиля
    if profile_created:
        profile_created = dt.datetime.fromtimestamp(profile_created).strftime('%A, %d %B %Y, %H:%M:%S')
    last_logoff = user.get('lastlogoff')  # время последнего входа
    if last_logoff:
        last_logoff = dt.datetime.fromtimestamp(last_logoff).strftime('%A, %d %B %Y, %H:%M:%S')

    # собираем информацию о блокировках пользователя
    bans_request = api_caller.ISteamUser.GetPlayerBans(steamids=steamid)
    community_ban = vac_ban = game_bans = economy_ban = None
    days_since_last_ban = 0

    if bans_request:
        bans = bans_request['players'][0]
        community_ban = bans['CommunityBanned']
        vac_ban = bans['NumberOfVACBans']
        game_bans = bans['NumberOfGameBans']
        economy_ban = bans["EconomyBan"] != "none"

        if community_ban or vac_ban or game_bans or economy_ban:
            # если есть какая-либо блокировка - мы можем узнать, когда она была
            # или когда была последняя блокировка
            days_since_last_ban = bans["DaysSinceLastBan"]

    # компонуем и возвращаем контейнер
    return SteamUser(steamid, nick, name, avatar, level, country, profile_created, last_logoff,
                     SteamUser.Bans(community_ban, vac_ban, game_bans, economy_ban, days_since_last_ban))


def get_app_details(appid):
    """Получаем информацию о приложении"""

    return requests.get('http://store.steampowered.com/api/appdetails/',
                        params={'appids': str(appid), 'cc': 'en', 'l': 'en'}).json()[str(appid)]


def get_friends(steamid: int):
    """Получаем список друзей пользователя"""

    try:
        friendslist_request = api_caller.ISteamUser.GetFriendList(steamid=steamid)
        if friendslist_request:
            friends_list = friendslist_request['friendslist']['friends']
            friends_steamids = ','.join(friend['steamid'] for friend in friends_list)
            friends_request = api_caller.ISteamUser.GetPlayerSummaries(steamids=friends_steamids)
            return [SteamUserFriend(friend['steamid'],
                                    friend['personaname'],
                                    friend['avatarfull']) for friend in friends_request['response']['players']]
    except requests.HTTPError:
        # если список друзей скрыт
        return


def get_games(steamid: int):
    """Получаем библиотеку пользователя"""

    try:
        games_request = api_caller.IPlayerService.GetOwnedGames(steamid=steamid, include_appinfo=True,
                                                                include_played_free_games=True, appids_filter=None,
                                                                include_free_sub=False, language='en',
                                                                include_extended_appinfo=False)
        if games_request and games_request.get('response'):
            return games_request['response']['games']
    except requests.ConnectionError:
        # если библиотека скрыта
        return


def get_730_stats(steamid):
    """Получаем статистику пользователя в CS:GO/CS2"""
    try:
        response = api_caller.ISteamUserStats.GetUserStatsForGame(appid=730, steamid=steamid)
        if response:
            stats_dict = {stat['name']: stat['value'] for stat in response["playerstats"]["stats"]}
            stats_dict['steamid'] = steamid
            return Appid730GameStats.from_dict(stats_dict)
    except requests.HTTPError:
        # если статистики нет или она скрыта
        return
