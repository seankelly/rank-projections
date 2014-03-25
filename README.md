# Rank Projections

A tool to average multiple projections for the purposes of ranking players for fantasy purposes. Supports using alternate playing time projections (e.g. Fans Scouting Reports) and will scale the appropriate stats to the new playing time projections.

## Usage
Pass the `-h` or `--help` option to list the options. Despite the name 'optional', most of the optional arguments are necessary.

The `--batting` and `--pitching` options declare the stats to use for batters and pitchers respectively. Use each option with a comma-separated list of the stats in your fantasy draft.

Pass a filename to `--output` to save the rankings. The output format will be CSV.

The `--playing-time` option is not required. It should be used for each separate playing time file (likely two). Any players found in these files will have their projected counting stats modified to account for the antipated playing time.

## Examples
    ./rank-projections.py -p IP,W,R,SO,WHIP -b R,HR,RBI,OBP,SLG,SB -o rank.csv -t data/2014\ Projections/player-time/Fans\ pitchers.csv -t data/2014\ Projections/player-time/Fans\ batters.csv data/2014\ Projections/\*.csv

## Bugs
* If a stat is used that is not present in all of the projections, a runtime error happens.
