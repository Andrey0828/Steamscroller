import datetime as dt
import json
import sys

import requests
import validators
from requests.exceptions import HTTPError
from steam.webapi import WebAPI
from country_name import search_country_name

import config as cfg


api = WebAPI(key=cfg.API_KEY)
request_url = 'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=' + cfg.API_KEY + '&vanityurl='

user_id: int
user_request = input('Enter Steam ID or Vanity URL or Nickname: ').strip()
if user_request.isnumeric() and len(user_request) == 17:
    user_id = int(user_request)
else:
    if validators.url(user_request):
        resolve_vanity = api.ISteamUser.ResolveVanityURL(vanityurl=user_request, url_type=1)['response']
        if resolve_vanity['success'] == 1:
            user_id = resolve_vanity['steamid']
        elif resolve_vanity['success'] == 42:
            print('No user with this Vanity URL found.')
            sys.exit()
        else:
            print('Failed to resolve Vanity URL, please try again.')
            sys.exit()
    else:
        response = requests.get(request_url + user_request)
        if response.status_code == 200:
            data = json.loads(response.text)['response']
            if data['success'] == 1:
                user_id = data['steamid']
            elif data['success'] == 42:
                print('No user with this nickname.')
                sys.exit()
            else:
                print('Error, please try again.')
                sys.exit()

print('\n----- User summary -----\n')
player_request = api.ISteamUser.GetPlayerSummaries(steamids=user_id)
player_request_level = api.IPlayerService.GetSteamLevel(steamid=user_id)
if player_request:
    user = player_request['response']['players'][0]
    level = player_request_level['response']['player_level']

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


def friends_parameters(fl):
    s = []
    for friend in fl:
        friend_request = api.ISteamUser.GetPlayerSummaries(steamids=friend['steamid'])
        user = friend_request['response']['players'][0]
        nick = user['personaname']
        name = user.get('realname')
        avatar = user.get('avatarfull')
        s.append([avatar, nick, name])
    return s


try:
    friendslist_request = api.ISteamUser.GetFriendList(steamid=user_id)
    if friendslist_request:
        friends_list = friendslist_request['friendslist']['friends']
        friends_list = friends_parameters(friends_list)
        for i in friends_list:
            if i[2] is None:
                print(f"URL Avatar: {i[0]}", f'Nickname: {i[1]}', sep='\n')
            else:
                print(f"URL Avatar: {i[0]}", f'Nickname: {i[1]}', f'Real name*: {i[2]}', sep='\n')
            print()
    else:
        print('This user hidden his friend list.')
except HTTPError:
    print('This user hidden his friend list.')

print('\n----- Owned games -----\n')
games_request = api.IPlayerService.GetOwnedGames(steamid=user_id, include_appinfo=True,
                                                 include_played_free_games=True, appids_filter=None,
                                                 include_free_sub=False, language='en',
                                                 include_extended_appinfo=False)
if games_request:
    games = games_request['response']['games']
    for game in games:
        name, playtime = game['name'], game['playtime_forever'] / 60
        last_time_played = dt.datetime.fromtimestamp(game['rtime_last_played']).strftime('%A, %d %B %Y, %H:%M:%S')
        if playtime > 0:
            print(f'{name} - {playtime:.1f} hours played (last launch: {last_time_played}).')
        else:
            print(f'{name} - no playtime.')
