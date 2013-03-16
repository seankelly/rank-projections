#!/usr/bin/env python

import argparse
import csv
import numpy as np
from collections import defaultdict
from itertools import chain


class Projection():
    def __init__(self, file, batting, pitching, playing_time):
        self.file = file
        self.batting = batting
        self.pitching = pitching
        self.players = {}
        self.is_batting = False
        self.is_pitching = False
        self.id_column = None
        self._load_playing_time(playing_time)
        self._load_players()

    def __iter__(self):
        for p in self.players:
            yield p

    def _load_playing_time(self, playing_time):
        # Don't bother classifying the players. Just record their PA or IP.
        player = {}
        for pt_file in playing_time:
            pt_csv = csv.reader(open(pt_file))
            in_body = False
            idx = None
            for row in pt_csv:
                if in_body:
                    player[row[-1]] = float(row[idx])
                else:
                    in_body = True
                    if 'IP' in row:
                        idx = row.index('IP')
                    elif 'PA' in row:
                        idx = row.index('PA')
        self.pt = player

    def _load_players(self):
        is_batting, is_pitching = False, False
        in_body = False
        csv_file = csv.reader(open(self.file))
        for row in csv_file:
            if in_body:
                self.players[row[id_col]] = self.map_stats(row)
                self.players[row[id_col]]['name'] = row[0]
            else:
                in_body = True
                if not self._classify_file(row):
                    break
                # Set after the file has been classified.
                id_col = self.id_column

    def map_stats(self, row):
        stats = {}
        if self.is_batting:
            stat_list = self.batting
        elif self.is_pitching:
            stat_list = self.pitching
        for stat in stat_list:
            stats[stat] = self.mapping[stat](row)
        return stats


    def _classify_file(self, row):
        headers = set(row)
        num_batting = len(self.batting & headers)
        num_pitching = len(self.pitching & headers)
        if num_batting > num_pitching:
            self.is_batting = True
            self._create_mapping(self.batting, row)
        elif num_pitching > num_batting:
            self.is_pitching = True
            self._create_mapping(self.pitching, row)
        else:
            print("Unable to determine how to parse {0}".format(self.file))
            return False
        return True

    def _create_mapping(self, stats, row):
        """
        Generate a best-fit mapping for any stats missing from the projection
        file.
        """
        mapping = {}
        # Create a stat => index mapping. This will be used in the mapping for
        # missing stats.
        header_map = {}
        for i, stat in enumerate(row):
            header_map[stat] = i
        # Try to find the column to use to identify players. When downloading
        # from FanGraphs, the playerid column is automatically added.
        for id_col in ['playerid', 'Name', 'name']:
            if id_col in header_map:
                self.id_column = header_map[id_col]
                break

        headers = set(row)
        # Start with a pass-through of stats that were found.
        for stat in (stats & headers):
            mapping[stat] = lambda r, s=stat: float(r[header_map[s]])
        missing_stats = stats - headers
        for stat in missing_stats:
            if stat == 'R':
                # If can't find runs and this is a pitching file, then assume
                # 8% of runs are unearned. If a batting file, then this is a
                # rather crappy projection if runs are not included.
                if self.is_pitching and 'ER' in headers:
                    mapping[stat] = lambda r: float(r[header_map['ER']])*1.08
            elif stat == 'NSB':
                # If SB and CS are available, use that.
                if 'SB' in headers and 'CS' in headers:
                    mapping[stat] = lambda r: (int(r[header_map['SB']]) -
                                               int(r[header_map['CS']]))
                # If just SB available, then assume a 25% caught rate. This
                # means a third of SB's will be 'lost'.
                elif 'SB' in headers:
                    mapping[stat] = lambda r: int(r[header_map['SB']])*0.333
            else:
                mapping[stat] = lambda r: None
        self.mapping = mapping


class Averaged():
    def __init__(self, projections):
        self.projections = projections
        self.batter = {}
        self.pitcher = {}
        self.players = defaultdict(lambda: {})
        self._classify_projections()
        self._average()

    def _classify_projections(self):
        self.batter_proj = []
        self.pitcher_proj = []
        names = {}
        for p in self.projections:
            if p.is_batting:
                self.batter_proj.append(p)
            elif p.is_pitching:
                self.pitcher_proj.append(p)
            for pl in p:
                names[pl] = p.players[pl]['name']
        # Determine common subset of players projected.
        reduce_fn = lambda x,y: set(x) & set(y)
        self.save_players = (reduce(reduce_fn, self.batter_proj) |
                             reduce(reduce_fn, self.pitcher_proj))
        self.names = names

    def _average(self):
        self._average_projection(self.batter_proj,
                self.batter_proj[0].batting)
        self._average_projection(self.pitcher_proj,
                self.pitcher_proj[0].pitching, True)

    def _average_projection(self, projections, stats, pitching=False):
        final = defaultdict(lambda: defaultdict(lambda: []))
        # For pitchers, certain stats are better the lower they are. List a few
        # to reverse if this is for pitchers.
        reverse_stats = set(['R', 'WHIP', 'ERA', 'BB'])
        for stat in stats:
            for proj in projections:
                players = sorted(proj.players)
                l = map(lambda p: proj.players[p][stat], players)
                a = np.array(l)
                if pitching and stat in reverse_stats:
                    a = -a
                sigma = np.std(a)
                mu = np.mean(a)
                zs = (a - mu)/sigma
                for i, pl in enumerate(players):
                    final[pl][stat].append(zs[i])
        for pl in final:
            if pl not in self.save_players:
                continue
            rating = 0
            for stat in final[pl]:
                r = np.mean(final[pl][stat])
                self.players[pl][stat] = r
                rating += r
            self.players[pl]['rank'] = rating
            self.players[pl]['name'] = self.names[pl]


def load_projections(batting, pitching, files, playing_time):
    projections = []
    for file in files:
        projections.append(Projection(file, batting, pitching, playing_time))
    return projections

def save_ranking(averaged, output_file, batting, pitching):
    players = averaged.players
    ordered = sorted(players, key=lambda x: players[x]['rank'], reverse=True)
    csv_out = csv.writer(open(output_file, 'w'))
    stats = list(chain(batting, pitching))
    # Print a header to help figure out the columns.
    csv_out.writerow(['Name', 'Rank'] + stats)
    for p in ordered:
        row = ([players[p]['name'], ("%.4f" % players[p]['rank'])]
               + map(lambda k: ("%.4f" % players[p].get(k, 0)), stats))
        csv_out.writerow(row)


def get_options():
    parser = argparse.ArgumentParser(description="Average MLB projections "
                "and rank the players in given stats.")
    parser.add_argument('-o', '--output',
                        help='Save ranked players')
    parser.add_argument('-b', '--batting',
                        help='Add batting stat')
    parser.add_argument('-p', '--pitching',
                        help='Add pitching stat')
    parser.add_argument('-t', '--playing-time', action='append',
                        help='Add playing time projection')
    parser.add_argument('projections', nargs='+',
                        help='Projections to average')
    args = parser.parse_args()
    return args

def run():
    args = get_options()
    batting_stats = set(args.batting.upper().split(','))
    pitching_stats = set(args.pitching.upper().split(','))
    if batting_stats is None:
        raise ValueError, "Batting stats not specified."
    if pitching_stats is None:
        raise ValueError, "Pitching stats not specified."

    projections = load_projections(batting_stats, pitching_stats,
            args.projections, args.playing_time)
    averaged = Averaged(projections)
    save_ranking(averaged, args.output, batting_stats, pitching_stats)

if __name__ == '__main__':
    run()
