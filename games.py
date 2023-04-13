from typing import NamedTuple


class Appid730GameStats(NamedTuple):
    steamid: int
    total_time_played: float
    total_kills: int
    total_deaths: int
    kd_ratio: float
    total_matches_played: int
    total_matches_won: int
    matches_win_percentage: float
    total_rounds_played: int
    total_wins_pistolround: int
    total_shots_fired: int
    total_shots_hit: int
    hit_accuracy: float
    headshots_percentage: float
    best_map_name: str
    best_map_win_percentage: float
    total_mvps: int
    total_money_earned: int
    total_rescued_hostages: int
    total_weapons_donated: int
    total_broken_windows: int
    total_damage_done: int
    total_planted_bombs: int
    total_defused_bombs: int
    total_kills_knife: int
    total_kills_hegrenade: int
    total_kills_molotov: int
    total_shots_taser: int
    total_kills_taser: int
    taser_accuracy: float
    total_kills_knife_fight: int
    total_kills_enemy_weapon: int
    total_kills_enemy_blinded: int
    total_kills_against_zoomed_sniper: int
    total_shots_ak47: int
    total_hits_ak47: int
    total_kills_ak47: int
    ak47_accuracy: float
    total_shots_m4a1: int
    total_hits_m4a1: int
    total_kills_m4a1: int
    m4a1_accuracy: float
    total_shots_awp: int
    total_hits_awp: int
    total_kills_awp: int
    awp_accuracy: float
    total_shots_glock: int
    total_hits_glock: int
    total_kills_glock: int
    glock_accuracy: float
    total_shots_hkp2000: int
    total_hits_hkp2000: int
    total_kills_hkp2000: int
    hkp2000_accuracy: float
    total_shots_p250: int
    total_hits_p250: int
    total_kills_p250: int
    p250_accuracy: float
    total_shots_elite: int
    total_hits_elite: int
    total_kills_elite: int
    elite_accuracy: float
    total_shots_fiveseven: int
    total_hits_fiveseven: int
    total_kills_fiveseven: int
    fiveseven_accuracy: float
    total_shots_tec9: int
    total_hits_tec9: int
    total_kills_tec9: int
    tec9_accuracy: float
    total_shots_deagle: int
    total_hits_deagle: int
    total_kills_deagle: int
    deagle_accuracy: float
    total_shots_mac10: int
    total_hits_mac10: int
    total_kills_mac10: int
    mac10_accuracy: float
    total_shots_mp7: int
    total_hits_mp7: int
    total_kills_mp7: int
    mp7_accuracy: float
    total_shots_mp9: int
    total_hits_mp9: int
    total_kills_mp9: int
    mp9_accuracy: float
    total_shots_ump45: int
    total_hits_ump45: int
    total_kills_ump45: int
    ump45_accuracy: float
    total_shots_bizon: int
    total_hits_bizon: int
    total_kills_bizon: int
    bizon_accuracy: float
    total_shots_p90: int
    total_hits_p90: int
    total_kills_p90: int
    p90_accuracy: float
    total_shots_famas: int
    total_hits_famas: int
    total_kills_famas: int
    famas_accuracy: float
    total_shots_galilar: int
    total_hits_galilar: int
    total_kills_galilar: int
    galilar_accuracy: float
    total_shots_aug: int
    total_hits_aug: int
    total_kills_aug: int
    aug_accuracy: float
    total_shots_sg556: int
    total_hits_sg556: int
    total_kills_sg556: int
    sg556_accuracy: float
    total_shots_ssg08: int
    total_hits_ssg08: int
    total_kills_ssg08: int
    ssg08_accuracy: float
    total_shots_scar20: int
    total_hits_scar20: int
    total_kills_scar20: int
    scar20_accuracy: float
    total_shots_g3sg1: int
    total_hits_g3sg1: int
    total_kills_g3sg1: int
    g3sg1_accuracy: float
    total_shots_nova: int
    total_hits_nova: int
    total_kills_nova: int
    nova_accuracy: float
    total_shots_mag7: int
    total_hits_mag7: int
    total_kills_mag7: int
    mag7_accuracy: float
    total_shots_sawedoff: int
    total_hits_sawedoff: int
    total_kills_sawedoff: int
    sawedoff_accuracy: float
    total_shots_xm1014: int
    total_hits_xm1014: int
    total_kills_xm1014: int
    xm1014_accuracy: float
    total_shots_negev: int
    total_hits_negev: int
    total_kills_negev: int
    negev_accuracy: float
    total_shots_m249: int
    total_hits_m249: int
    total_kills_m249: int
    m249_accuracy: float

    @classmethod
    def from_dict(cls, stats: dict):
        WEAPONS = ('ak47', 'm4a1', 'awp', 'glock', 'hkp2000', 'p250', 'elite', 'fiveseven',
                   'tec9', 'deagle', 'mac10', 'mp7', 'mp9', 'ump45', 'bizon', 'p90', 'famas',
                   'galilar', 'aug', 'sg556', 'ssg08', 'scar20', 'g3sg1', 'nova', 'mag7', 'sawedoff',
                   'xm1014', 'negev', 'm249')

        stats['total_time_played'] = round(stats["total_time_played"] / 3600, 2)
        stats['kd_ratio'] = round(stats['total_kills'] / stats['total_deaths'], 2)
        stats['matches_win_percentage'] = round(stats['total_matches_won'] / stats['total_matches_played'] * 100,
                                                2)
        stats['hit_accuracy'] = round(stats['total_shots_hit'] / stats['total_shots_fired'] * 100, 2)
        stats['headshots_percentage'] = round(stats['total_kills_headshot'] / stats['total_kills'] * 100, 2)

        best_map = max((stat for stat in stats if stat.startswith('total_wins_map_')),
                       key=lambda x: stats[x]).split('_')[-2:]
        stats['best_map_name'] = best_map[-1].capitalize()
        best_map_wins = stats[f'total_wins_map_{"_".join(best_map)}']
        best_map_rounds = stats[f'total_rounds_map_{"_".join(best_map)}']
        stats['best_map_win_percentage'] = round(best_map_wins / best_map_rounds * 100, 2)

        stats['taser_accuracy'] = round(stats['total_kills_taser'] / stats[f'total_shots_taser'] * 100, 2)

        for weapon in WEAPONS:
            stats[f'{weapon}_accuracy'] = \
                round(stats[f'total_hits_{weapon}'] / stats[f'total_shots_{weapon}'] * 100, 2)

        stats = {k: v for k, v in stats.items() if k in cls._fields}

        return cls(**stats)

    def stats_only(self):
        return tuple(stat for field, stat in zip(self._fields, self) if field != 'steamid')

    def get_text(self):
        return """<div class="stats-container">
                    <div class="stats-category">
                        <h3>📊 General in-game statistics:</h3>
                        <ul>
                            <li>Playtime (matchmaking): <b>{:,}</b> hours</li>
                            <li>Kills: <b>{:,}</b></li>
                            <li>Deaths: <b>{:,}</b></li>
                            <li>K/D ratio: <b>{}</b></li>
                        </ul>
                        <br>
                        <ul>
                            <li>Matches played: <b>{:,}</b></li>
                            <li>Matches won: <b>{:,}</b></li>
                            <li>Win percentage: <b>{}</b>%</li>
                            <li>Rounds played: <b>{:,}</b></li>
                            <li>Pistol rounds won: <b>{:,}</b></li>
                        </ul>
                    </div>
        
                    <div class="stats-category">
                        <h3>🔫 Shooting statistics:</h3>
                        <ul>
                            <li>Shots: <b>{:,}</b></li>
                            <li>Hits: <b>{:,}</b></li>
                            <li>Fire accuracy: <b>{}</b>%</li>
                            <li>Headshot accuracy: <b>{}</b>%</li>
                        </ul>
                    </div>
        
                    <div class="stats-category">
                        <h3>🗺️ Map statistics:</h3>
                        <ul>
                            <li>Best map: <b>{}</b></li>
                            <li>Win percentage: <b>{}</b>%</li>
                        </ul>
                    </div>
        
                    <div class="stats-category">
                        <h3>🔰 Misc:</h3>
                        <ul>
                            <li>MVPs: <b>{:,}</b></li>
                            <li>Money earned: <b>{:,}</b>$</li>
                            <li>Hostages rescued: <b>{:,}</b></li>
                            <li>Weapons donated: <b>{:,}</b></li>
                            <li>Windows broken: <b>{:,}</b></li>
                        </ul>
                        <br>
                        <ul>
                            <li>Damage done: <b>{:,}</b></li>
                            <li>Bombs planted: <b>{:,}</b></li>
                            <li>Bombs defused: <b>{:,}</b></li>
                        </ul>
                        <br>
                        <ul>
                            <li>Knife kills: <b>{:,}</b></li>
                            <li>HE grenade kills: <b>{:,}</b></li>
                            <li>Molotov kills: <b>{:,}</b></li>
                        </ul>
                        <br>
                        <ul>
                            <li>Zeus shots: <b>{:,}</b></li>
                            <li>Zeus kills: <b>{:,}</b></li>
                            <li>Zeus fire accuracy: <b>{}</b>%</li>
                        </ul>
                        <br>
                        <ul>
                            <li>Knife fights won: <b>{:,}</b></li>
                            <li>Kills with enemy weapons: <b>{:,}</b></li>
                            <li>Blind enemies killed: <b>{:,}</b></li>
                            <li>Zoomed snipers killed: <b>{:,}</b></li>
                        </ul>
                    </div>
        
                    <div class="stats-category"><h3>🔫 Gun statistics:</h3>
                        <div class="stats-subcategory"><h4>AK-47:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>M4A4 / M4A1-S:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>AWP:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                    </div>
        
                    <div class="stats-category"><h3>🔫 Pistol statistics:</h3>
                        <div class="stats-subcategory"><h4>Glock-18:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>USP-S / P2000:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>P250:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>Dual Berettas:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>Five-SeveN / CZ75-Auto:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>Tec-9 / CZ75-Auto:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>Desert Eagle / R8 Revolver:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                    </div>
        
                    <div class="stats-category"><h3>🔫 SMG statistics:</h3>
                        <div class="stats-subcategory"><h4>MAC-10:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>MP7 / MP5-SD:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>MP9:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>UMP-45:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>PP-Bizon:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>P90:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                    </div>
        
                    <div class="stats-category"><h3>🔫 Rifle statistics:</h3>
                        <div class="stats-subcategory"><h4>FAMAS:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>Galil AR:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>AUG:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>SG 553:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                    </div>
        
                    <div class="stats-category"><h3>🔫 Sniper rifle statistics:</h3>
                        <div class="stats-subcategory"><h4>SSG 08:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>SCAR-20:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>G3SG1:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                    </div>
        
                    <div class="stats-category"><h3>🔫 Heavy gun statistics:</h3>
                        <div class="stats-subcategory"><h4>Nova:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>MAG-7:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>Sawed-Off:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>XM1014:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>Negev:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                        <div class="stats-subcategory"><h4>M249:</h4>
                            <ul>
                                <li>Shots: <b>{:,}</b></li>
                                <li>Hits: <b>{:,}</b></li>
                                <li>Kills: <b>{:,}</b></li>
                                <li>Fire accuracy: <b>{}</b>%</li>
                            </ul>
                        </div>
                    </div>
                </div>""".format(*self.stats_only())