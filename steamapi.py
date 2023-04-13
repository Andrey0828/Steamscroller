import requests
from steam.webapi import WebAPI

import config as cfg
from games import Appid730GameStats

api_caller = WebAPI(key=cfg.API_KEY)


def get_app_details(appid) -> dict | None:
    return requests.get('http://store.steampowered.com/api/appdetails/',
                        params={'appids': str(appid), 'cc': 'en', 'l': 'en'}).json()


def get_friends(steamid) -> list | None:
    friendslist_request = api_caller.ISteamUser.GetFriendList(steamid=steamid)
    if friendslist_request:
        friends_list = friendslist_request['friendslist']['friends']
        friends_steamids = ','.join(friend['steamid'] for friend in friends_list)
        friends_request = api_caller.ISteamUser.GetPlayerSummaries(steamids=friends_steamids)
        return friends_request['response']['players']


def get_games(steamid) -> list | None:
    games_request = api_caller.IPlayerService.GetOwnedGames(steamid=steamid, include_appinfo=True,
                                                            include_played_free_games=True, appids_filter=None,
                                                            include_free_sub=False, language='en',
                                                            include_extended_appinfo=False)
    if games_request:
        return games_request['response']['games']


def get_730_stats(steamid) -> Appid730GameStats | None:
    response = api_caller.ISteamUserStats.GetUserStatsForGame(appid=730, steamid=76561198260803063)
    if response:
        stats_dict = {stat['name']: stat['value'] for stat in response["playerstats"]["stats"]}
        stats_dict['steamid'] = steamid
        return Appid730GameStats.from_dict(stats_dict)
