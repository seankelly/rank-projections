#!/usr/bin/env python

import argparse
import csv
from collections import namedtuple

Batter = namedtuple('Batter', 'x')
Pitcher = namedtuple('Pitcher', 'x')

class Projection():
    def __init__(self, file, batting, pitching):
        self.file = file
        self.batting = batting
        self.pitching = pitching
        self.players = []
        self.is_batting = False
        self.is_pitching = False
        self.id_column = None
        self._load_players()

    def _load_players(self):
        is_batting, is_pitching = False, False
        in_body = False
        csv_file = csv.reader(open(self.file))
        for row in csv_file:
            if in_body:
                self.players.append(self.map_stats(row))
            else:
                in_body = True
                if not self._classify_file(row):
                    break

    def map_stats(self, row):
        stats = []
        if self.is_batting:
            for stat in self.batting:
                stats.append(self.mapping[stat](row))
            return Batter(*stats)
        elif self.is_pitching:
            for stat in self.pitching:
                stats.append(self.mapping[stat](row))
            return Pitcher(*stats)

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

def update_namedtuples(batting, pitching):
    global Batter, Pitcher
    Batter = namedtuple('Batter', batting)
    Pitcher = namedtuple('Pitcher', pitching)

def load_projections(batting, pitching, files):
    projections = []
    for file in files:
        projections.append(Projection(file, batting, pitching))

def average_projections(projections):
    pass

def rank_players(batting, pitching, projections):
    pass

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

    update_namedtuples(batting_stats, pitching_stats)
    load_projections(batting_stats, pitching_stats, args.projections)

if __name__ == '__main__':
    run()
