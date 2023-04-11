import datetime as dt
import re
import sys

import validators
from requests.exceptions import HTTPError
from steam.steamid import SteamID
from country_name import search_country_by_name

import steamapi

steam_profile_link_pattern = re.compile(r'(?:https?://)?steamcommunity\.com/(?:profiles|id)/[a-zA-Z0-9]+(/?)\w')


def main():
    user_id: int
    user_request = input('Enter Steam ID or Vanity URL: ').strip()

    if validators.url(user_request):
        if steam_profile_link_pattern.match(user_request):
            link_parts = steam_profile_link_pattern.match(user_request).group(0).split('/')
            user_request = link_parts[-1]
        else:
            print(f'Got wrong link. Please check is it correct and try again.')
            sys.exit()

    if SteamID(user_request).is_valid():
        user_id = int(user_request)
    else:
        resolve_vanity = steamapi.api_caller.ISteamUser.ResolveVanityURL(vanityurl=user_request, url_type=1)['response']
        if resolve_vanity['success'] == 1:
            user_id = resolve_vanity['steamid']
        elif resolve_vanity['success'] == 42:
            print('No user with this Vanity URL found.')
            sys.exit()
        else:
            print(f'Failed to resolve Vanity URL, please try again. ({resolve_vanity["success"]})')
            sys.exit()

    print('\n----- User summary -----\n')
    player_request = steamapi.api_caller.ISteamUser.GetPlayerSummaries(steamids=user_id)
    if player_request:
        user = player_request['response']['players'][0]
        level = steamapi.api_caller.IPlayerService.GetSteamLevel(steamid=user_id)['response']['player_level']

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
            print(f'Country: {search_country_by_name(country).name}')
        if level:
            print(f'User level: {level}')
        print()
        print(f'Profile created: {profile_created}')
        if last_logoff:
            last_logoff = dt.datetime.fromtimestamp(user['lastlogoff']).strftime('%A, %d %B %Y, %H:%M:%S')
            print(f'Last logoff: {last_logoff}')

        bans_request = steamapi.api_caller.ISteamUser.GetPlayerBans(steamids=user_id)
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
        friends = steamapi.get_friends(user_id)
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
    games = steamapi.get_games(user_id)
    if games:
        print('==============================')
        for game in games:
            # game_detailed_info = steamapi.get_app_details(game['appid'])
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
