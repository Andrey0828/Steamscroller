import datetime as dt
import re
import sys

import requests
import validators
from requests.exceptions import HTTPError
from steam.webapi import WebAPI
from steam.steamid import SteamID
from country_name import search_country_name

import config as cfg


api = WebAPI(key=cfg.API_KEY)
link_pattern = re.compile(r'(?:https?://)?steamcommunity\.com/(?:profiles|id)/[a-zA-Z0-9]+(/?)\w')
app_details_request_url = 'http://store.steampowered.com/api/appdetails/'


def get_friends(steamid) -> list | None:
    friendslist_request = api.ISteamUser.GetFriendList(steamid=steamid)
    if friendslist_request:
        friends_list = friendslist_request['friendslist']['friends']
        friends_steamids = ','.join(friend['steamid'] for friend in friends_list)
        friends_request = api.ISteamUser.GetPlayerSummaries(steamids=friends_steamids)
        return friends_request['response']['players']


def get_games(steamid) -> list | None:
    games_request = api.IPlayerService.GetOwnedGames(steamid=steamid, include_appinfo=True,
                                                     include_played_free_games=True, appids_filter=None,
                                                     include_free_sub=False, language='en',
                                                     include_extended_appinfo=False)
    if games_request:
        return games_request['response']['games']


def main():
    user_id: int
    user_request = input('Enter Steam ID or Vanity URL: ').strip()

    if validators.url(user_request):
        if link_pattern.match(user_request):
            link_parts = link_pattern.match(user_request).group(0).split('/')
            user_request = link_parts[-1]
        else:
            print(f'Got wrong link. Please check is it correct and try again.')
            sys.exit()

    if SteamID(user_request).is_valid():
        user_id = int(user_request)
    else:
        resolve_vanity = api.ISteamUser.ResolveVanityURL(vanityurl=user_request, url_type=1)['response']
        if resolve_vanity['success'] == 1:
            user_id = resolve_vanity['steamid']
        elif resolve_vanity['success'] == 42:
            print('No user with this Vanity URL found.')
            sys.exit()
        else:
            print(f'Failed to resolve Vanity URL, please try again. ({resolve_vanity["success"]})')
            sys.exit()

    print('\n----- User summary -----\n')
    player_request = api.ISteamUser.GetPlayerSummaries(steamids=user_id)
    if player_request:
        user = player_request['response']['players'][0]
        level = api.IPlayerService.GetSteamLevel(steamid=user_id)['response']['player_level']

        nick = user['personaname']
        name = user.get('realname')
        avatar = user.get('avatarfull')
        country = user.get('loccountrycode')
        profile_created = dt.datetime.fromtimestamp(user['timecreated']).strftime('%A, %d %B %Y, %H:%M:%S')
        last_logoff = user.get('lastlogoff')

        print(f'URL Avatar: {avatar}')
        print(f'Nickname: {nick}')
        if name:
            print(f'Real name*: {name}')
        if country:
            print(f'Country: {search_country_name(country)}')
        if level:
            print(f'User level: {level}')
        print()
        print(f'Profile created: {profile_created}')
        if last_logoff:
            last_logoff = dt.datetime.fromtimestamp(user['lastlogoff']).strftime('%A, %d %B %Y, %H:%M:%S')
            print(f'Last logoff: {last_logoff}')

        bans_request = api.ISteamUser.GetPlayerBans(steamids=user_id)
        if bans_request:
            bans = bans_request['players'][0]
            community_ban, vac_ban = bans['CommunityBanned'], bans['VACBanned']
            game_bans = bans['NumberOfGameBans']
            economy_ban = bans["EconomyBan"] != "none"

            print(f'Game bans: {game_bans if game_bans else "No"}')
            print(f'Community ban: {"Yes" if community_ban else "No"}')
            print(f'VAC bans: {bans["NumberOfVACBans"] if vac_ban else "No"}')
            print(f'Economy ban: {"Yes" if economy_ban else "No"}')

            if community_ban or vac_ban or game_bans or economy_ban:
                print(f'Days since last ban: {bans["DaysSinceLastBan"]}')

        if name:
            print('\n* - User real name are defined by a user itself.')

    print('\n----- Friends (WIP) -----\n')

    try:
        friends = get_friends(user_id)
        if friends:
            for friend in friends:
                steamid = friend['steamid']
                nick = friend['personaname']
                name = friend.get('realname')
                avatar = friend['avatarfull']

                print(f'URL Avatar: {avatar}')
                print(f'Nickname: {nick}')
                print(f'SteamID: {steamid}')
                if name:
                    print(f'Real name*: {name}')
                    print('\n* - User real name are defined by a user itself.')
                print()
        else:
            print('This user hidden his friend list.')
    except HTTPError:
        print('This user hidden his friend list.')

    print('\n----- Owned games -----\n')
    games = get_games(user_id)
    if games:
        print('==============================')
        for game in games:
            # game_detailed_info = requests.get(app_details_request_url,
            #                                   params={'appids': str(game['appid']), 'cc': 'en', 'l': 'en'}).json()

            name, playtime = game['name'], game['playtime_forever'] / 60
            last_time_played = dt.datetime.fromtimestamp(game['rtime_last_played']).strftime('%A, %d %B %Y, %H:%M:%S')
            # print(game_detailed_info)
            if playtime > 0:
                print(f'{name} - {playtime:.1f} hours played (last launch: {last_time_played}).')
            else:
                print(f'{name} - no playtime.')
    else:
        print('This user doesn\'t own any game or hidden his games list.')


if __name__ == '__main__':
    main()
