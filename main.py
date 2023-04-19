import datetime as dt
import re
from typing import NamedTuple

import requests
from steam.steamid import SteamID
from country_name import search_country_by_name
from game_search import search_game_on_steam
import steamapi

import config as cfg

from flask import Flask, render_template, redirect, request, url_for, abort

TITLE = 'Steamscroller'
app = Flask(__name__)
app.config['SECRET_KEY'] = cfg.FLASKAPP_SECRET_KEY


steam_profile_link_pattern = re.compile(r'(?:https?://)?steamcommunity\.com/(?:profiles|id)/[a-zA-Z0-9]+(/?)\w')


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('404.html'), 404


@app.route("/")
def index():
    return render_template("index.html", title=TITLE)


@app.route("/profiles/<int:steamid>/cs2stats/")
@app.route("/profiles/<int:steamid>/csgostats/")
@app.route("/profiles/<int:steamid>/730stats/")
def steam_profile_730stats(steamid: int):
    if not SteamID(steamid).is_valid():
        return 'User not found.'

    player_request = steamapi.api_caller.ISteamUser.GetPlayerSummaries(steamids=steamid)["response"]["players"]
    if not player_request:
        return 'User not found.'

    user = player_request[0]
    nick = user['personaname']
    avatar = user.get('avatarfull')

    stats = steamapi.get_730_stats(steamid)
    if not stats:
        return 'Failed to get stats.'

    return render_template('steam_profile_730_stats.html', title=f"{TITLE} :: {nick}",
                           nick=nick, avatar=avatar, stats=stats.get_text())


@app.route("/profiles/<int:steamid>/games/", methods=['POST', 'GET'])
def steam_profile_games(steamid: int):
    if request.method == 'POST':
        if 'user730stats' in request.form:
            return redirect(url_for('steam_profile_730stats', steamid=steamid))

    if not SteamID(steamid).is_valid():
        return 'User not found.'

    player_request = steamapi.api_caller.ISteamUser.GetPlayerSummaries(steamids=steamid)["response"]["players"]
    if not player_request:
        return 'User not found.'

    user = player_request[0]
    nick = user['personaname']
    avatar = user.get('avatarfull')

    games = steamapi.get_games(steamid)

    return render_template('steam_profile_games.html', title=f"{TITLE} :: {nick}",
                           nick=nick, avatar=avatar, games=games)


@app.route("/profiles/<int:steamid>/", methods=['POST', 'GET'])
def steam_profile(steamid: int):
    if request.method == 'POST':
        if 'usergames' in request.form:
            return redirect(url_for('steam_profile_games', steamid=steamid))

    if not SteamID(steamid).is_valid():
        return 'User not found.'

    player_request = steamapi.api_caller.ISteamUser.GetPlayerSummaries(steamids=steamid)["response"]["players"]
    if not player_request:
        return 'User not found.'

    user = player_request[0]
    level = steamapi.api_caller.IPlayerService.GetSteamLevel(steamid=steamid)['response']['player_level']

    class Bans(NamedTuple):
        community_ban: bool
        vac_bans: int
        game_bans: int
        economy_ban: bool
        days_since_last_ban: int

    class User(NamedTuple):
        nick: str
        name: str | None
        avatar: str
        level: int | None
        country: str | None
        profile_created: str
        last_logoff: str | None
        bans: Bans

    nick = user['personaname']
    name = user.get('realname')
    avatar = user.get('avatarfull')
    country = user.get('loccountrycode')
    if country:
        country = search_country_by_name(country).name
    profile_created = dt.datetime.fromtimestamp(user['timecreated']).strftime('%A, %d %B %Y, %H:%M:%S')
    last_logoff = user.get('lastlogoff')
    if last_logoff:
        last_logoff = dt.datetime.fromtimestamp(last_logoff).strftime('%A, %d %B %Y, %H:%M:%S')

    bans_request = steamapi.api_caller.ISteamUser.GetPlayerBans(steamids=steamid)
    community_ban, vac_ban, game_bans, economy_ban = None, None, None, None
    days_since_last_ban = 0

    if bans_request:
        bans = bans_request['players'][0]
        community_ban = bans['CommunityBanned']
        vac_ban = bans['NumberOfVACBans']
        game_bans = bans['NumberOfGameBans']
        economy_ban = bans["EconomyBan"] != "none"

        if community_ban or vac_ban or game_bans or economy_ban:
            days_since_last_ban = bans["DaysSinceLastBan"]

    return render_template('steam_profile.html', title=f"{TITLE} :: {nick}",
                           user=User(nick, name, avatar, level, country, profile_created, last_logoff,
                                     Bans(community_ban, vac_ban, game_bans, economy_ban, days_since_last_ban)))


@app.route("/id/<string:vanityurl>/", strict_slashes=False)
def steam_profile_vanity(vanityurl: str):
    resolve_vanity = steamapi.api_caller.ISteamUser.ResolveVanityURL(vanityurl=vanityurl, url_type=1)['response']

    if resolve_vanity['success'] == 1:
        return redirect(url_for('steam_profile', steamid=resolve_vanity["steamid"]))

    if resolve_vanity['success'] == 42:
        return 'User not found.'

    return f'Error! Try again later. ({resolve_vanity["success"]})'


@app.route('/searchapp/<string:query>')
def search_app(query: str):
    return search_apps_by_name(query)


@app.route("/app/<int:appid>/")
def app_page(appid: int):
    result = search_game_on_steam(appid)
    if result == 'not found':
        return abort(404)

    result['developers'] = ', '.join(result['developers'])
    result['genres'] = ', '.join(genre['description'] for genre in result['genres'])
    result['categories'] = ', '.join(genre['description'] for genre in result['categories'])
    if result['price'] == 0:
        result['price'] = 'free'
    return render_template("steam_app.html", title=f'{TITLE} :: {result["name"]}', **result)


@app.route("/livesearch", methods=["POST", "GET"])
def livesearch():
    query = request.form.get("query")
    if query is None:
        return redirect('/')
    return search_apps_by_name(query)[:10]


def search_apps_by_name(name: str):
    requested_name = name.strip().lower()
    response = requests.get('http://api.steampowered.com/ISteamApps/GetAppList/v0002/?type=game',
                            params={'key': cfg.API_KEY})
    if response.status_code != 200:
        return f'Error! Try again later. ({response.status_code})'

    apps = response.json()['applist']['apps']
    results = (_app for _app in apps if requested_name in _app['name'].strip().lower())
    results = sorted(results, key=lambda x: (x['name'].lower().index(requested_name), x['appid']))
    return results[:2000]


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
