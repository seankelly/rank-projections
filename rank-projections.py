#!/usr/bin/env python

import argparse
import csv
from collections import namedtuple

Batter = namedtuple('Batter', 'x')
Pitcher = namedtuple('Pitcher', 'x')

class Projection():
    def __init__(self, file, batting, pitching):
        self.file = file
        self.players = []

    def _load_players(self):
        pass

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
    parser.add_argument('-b', '--batting', action='append',
                        help='Add batting stat')
    parser.add_argument('-p', '--pitching', action='append',
                        help='Add pitching stat')
    parser.add_argument('-t', '--playing-time', action='append',
                        help='Add playing time projection')
    parser.add_argument('projections', nargs='+',
                        help='Projections to average')
    args = parser.parse_args()
    return args

def run():
    args = get_options()
    batting_stats = args.batting
    pitching_stats = args.pitching
    if batting_stats is None:
        raise ValueError, "Batting stats not specified."
    if pitching_stats is None:
        raise ValueError, "Pitching stats not specified."

    update_namedtuples(batting_stats, pitching_stats)
    load_projections(batting_stats, pitching_stats, args.projections)

if __name__ == '__main__':
    run()
