#!/usr/bin/env python

import argparse
import csv
from collections import namedtuple

class Projection():
    def __init__(self, file, *stats):
        self.file = file
        self.players = []

    def _load_players(self):
        pass


def get_options():
    parser = argparse.ArgumentParser(description="Average MLB projections "
                "and rank the players in given stats.")
    args = parser.parse_args()

if __name__ == '__main__':
    args = get_options()
