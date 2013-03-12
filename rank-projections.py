#!/usr/bin/env python

import argparse
import csv
from collections import namedtuple

Batter = namedtuple('Batter', 'x')
Pitcher = namedtuple('Pitcher', 'x')

class Projection():
    def __init__(self, file, *stats):
        self.file = file
        self.players = []

    def _load_players(self):
        pass

def load_projections():
    pass

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

if __name__ == '__main__':
    args = get_options()
