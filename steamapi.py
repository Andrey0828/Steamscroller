from typing import NamedTuple
import datetime as dt

import requests
from steam.steamid import SteamID
from steam.webapi import WebAPI

import config as cfg
from games import Appid730GameStats
from country_name import search_country_by_name

api_caller = WebAPI(key=cfg.API_KEY)

"""Обозначение типа переменных"""


class SteamUser(NamedTuple):
    class Bans(NamedTuple):
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
    id: int
    nickname: str
    avatar: str


"""Получение сведений об пользователе"""


def get_user(steamid: int):
    if not SteamID(steamid).is_valid():
        return

    player_request = api_caller.ISteamUser.GetPlayerSummaries(steamids=steamid)["response"]["players"]
    if not player_request:
        return

    user = player_request[0]
    level = api_caller.IPlayerService.GetSteamLevel(steamid=steamid)['response'].get('player_level')

    nick = user['personaname']  # никнейм
    name = user.get('realname')  # имя
    avatar = user.get('avatarfull')  # аватар
    country = user.get('loccountrycode')  # код страны
    if country:
        country = search_country_by_name(country)
        if country:
            country = country.name
    profile_created = user.get('timecreated')  # время создания профиля
    if profile_created:
        profile_created = dt.datetime.fromtimestamp(profile_created).strftime('%A, %d %B %Y, %H:%M:%S')
    last_logoff = user.get('lastlogoff')  # время последнего входа
    if last_logoff:
        last_logoff = dt.datetime.fromtimestamp(last_logoff).strftime('%A, %d %B %Y, %H:%M:%S')

    bans_request = api_caller.ISteamUser.GetPlayerBans(steamids=steamid)
    community_ban = vac_ban = game_bans = economy_ban = None
    days_since_last_ban = 0

    # Наличие банов
    if bans_request:
        bans = bans_request['players'][0]
        community_ban = bans['CommunityBanned']
        vac_ban = bans['NumberOfVACBans']
        game_bans = bans['NumberOfGameBans']
        economy_ban = bans["EconomyBan"] != "none"

        if community_ban or vac_ban or game_bans or economy_ban:
            days_since_last_ban = bans["DaysSinceLastBan"]

    return SteamUser(steamid, nick, name, avatar, level, country, profile_created, last_logoff,
                     SteamUser.Bans(community_ban, vac_ban, game_bans, economy_ban, days_since_last_ban))


"""Получение деталей об игре"""


def get_app_details(appid):
    return requests.get('http://store.steampowered.com/api/appdetails/',
                        params={'appids': str(appid), 'cc': 'en', 'l': 'en'}).json()[str(appid)]


"""Получение списка друзей"""


def get_friends(steamid: int):
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
        return


"""Получение списка игр"""


def get_games(steamid: int):
    try:
        games_request = api_caller.IPlayerService.GetOwnedGames(steamid=steamid, include_appinfo=True,
                                                                include_played_free_games=True, appids_filter=None,
                                                                include_free_sub=False, language='en',
                                                                include_extended_appinfo=False)
        if games_request and games_request.get('response'):
            return games_request['response']['games']
    except requests.ConnectionError:
        return


"""Получение статистики в игре"""


def get_730_stats(steamid):
    try:
        response = api_caller.ISteamUserStats.GetUserStatsForGame(appid=730, steamid=steamid)
        if response:
            stats_dict = {stat['name']: stat['value'] for stat in response["playerstats"]["stats"]}
            stats_dict['steamid'] = steamid
            return Appid730GameStats.from_dict(stats_dict)
    except requests.HTTPError:
        return
