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
        self._load_players()

    def _load_players(self):
        is_batting, is_pitching = False, False
        in_body = False
        csv_file = csv.reader(open(self.file))
        for row in csv_file:
            if in_body:
                pass
            else:
                in_body = True
                headers = set(row)
                num_batting = len(self.batting & headers)
                num_pitching = len(self.pitching & headers)
                if num_batting > num_pitching:
                    is_batting = True
                    self._create_mapping(self.batting, headers)
                elif num_pitching > num_batting:
                    is_pitching = True
                    self._create_mapping(self.pitching, headers)
                else:
                    print("Unable to determine how to parse {0}".format(self.file))
                    break

    def _create_mapping(self, stats, headers):
        """
        Generate a best-fit mapping for any stats missing from the projection
        file.
        """
        mapping = {}
        # Start with a pass-through of stats that were found.
        for stat in (stats & headers):
            mapping[stat] = lambda x: x
        missing_stats = stats - headers
        for stat in missing_stats:
            # If can't find runs and this is a pitching file, then assume 8% of
            # runs are unearned.
            if stat == 'R':
                if self.is_pitching:
                    mapping[stat] = lambda x: x/1.08

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
