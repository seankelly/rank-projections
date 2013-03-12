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


def get_options():
    parser = argparse.ArgumentParser(description="Average MLB projections "
                "and rank the players in given stats.")
    parser.add_argument('-f', '--file',
                        help='Save ranked players')
    parser.add_argument('-o', '--offense', action='append',
                        help='Add offensive stat')
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
