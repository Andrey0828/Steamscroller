import datetime as dt
import sys

from requests.exceptions import HTTPError
from steam.webapi import WebAPI

import config as cfg


api = WebAPI(key=cfg.API_KEY)

user_id: int
user_request = input('Enter Steam ID or Vanity URL: ').strip()
if user_request.isnumeric() and len(user_request) == 17:
    user_id = int(user_request)
else:
    resolve_vanity = api.ISteamUser.ResolveVanityURL(vanityurl=user_request, url_type=1)['response']
    if resolve_vanity['success'] == 1:
        user_id = resolve_vanity['steamid']
    elif resolve_vanity['success'] == 42:
        print('No user with this Vanity URL found.')
        sys.exit()
    else:
        print('Failed to resolve Vanity URL, please try again.')
        sys.exit()

print('\n----- User summary -----\n')
player_request = api.ISteamUser.GetPlayerSummaries(steamids=user_id)
if player_request:
    user = player_request['response']['players'][0]

    nick = user['personaname']
    name = user.get('realname')
    profile_created = dt.datetime.fromtimestamp(user['timecreated']).strftime('%A, %d %B %Y, %H:%M:%S')
    last_logoff = user.get('lastlogoff')

    print(f'Nickname: {nick}')
    if name:
        print(f'Real name*: {name}')
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
    friendslist_request = api.ISteamUser.GetFriendList(steamid=user_id)
    if friendslist_request:
        friends_list = friendslist_request['friendslist']['friends']
        print(*friends_list, sep='\n')
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
