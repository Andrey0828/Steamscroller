import datetime as dt
import re
from typing import NamedTuple

from steam.steamid import SteamID
from country_name import search_country_by_name
from game_search import search_game_on_steam
import steamapi

import config as cfg

from flask import Flask, render_template, redirect, request, url_for, abort

TITLE = 'Steamscroller'
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = cfg.FLASKAPP_SECRET_KEY


steam_profile_link_pattern = re.compile(r'(?:https?://)?steamcommunity\.com/(?:profiles|id)/[a-zA-Z0-9]+(/?)\w')


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.errorhandler(501)
def internal_server_error(e):
    return render_template('501.html'), 501


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


@app.route("/profiles/<string:game_name>/")
def search_game(game_name: str):
    try:
        description, system = search_game_on_steam(game_name)
        par = description.get("recommended_system_requirements")
        if par is None:
            par = description.get("minimum_system_requirements")
        if "Processor" in par:
            par = par.replace("Processor", "#Processor")
        if "Memory" in par:
            par = par.replace("Memory", "#Memory")
        if "Graphics" in par:
            par = par.replace("Graphics", "#Graphics")
        if "Storage" in par:
            par = par.replace("Storage", "#Storage")
        if "Network" in par:
            par = par.replace("Network", "#Network")
        if system == "window":
            if "DirectX:" in par:
                par = par.replace("DirectX:", "#DirectX:")
        elif system == "linux":
            if "Sound Card:" in par:
                par = par.replace("Sound Card:", "#Sound Card:")
        parametrs = par.split("#")
        return render_template("steam_game.html", title=TITLE, **description, spisok_par=parametrs)
    except ValueError:
        description = search_game_on_steam(game_name)
        if description == 'Игра не найдена':
            abort(500)
        elif description == 'Данный товар недоступен в вашем регионе':
            abort(501)


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
