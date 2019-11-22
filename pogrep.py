#!/usr/bin/env python3
"""Find translations exemples by grepping in .po files.
"""

__version__ = "0.1.1"

import argparse
import curses
from glob import glob
import os
from textwrap import fill

import regex
import polib
from tabulate import tabulate


def red_color():
    """Just returns the CSI codes for red and reset color.
    """
    try:
        curses.setupterm()
        fg_color = curses.tigetstr("setaf") or curses.tigetstr("setf") or ""
        red = str(curses.tparm(fg_color, 1), "ascii")
        no_color = str(curses.tigetstr("sgr0"), "ascii")
    except Exception:
        red = ""
        no_color = ""
    return red, no_color


RED, NO_COLOR = red_color()


def get_term_width():
    scr = curses.initscr()
    width = scr.getmaxyx()[1]
    curses.endwin()
    return width


WIDTH = get_term_width()


def colorize(text, pattern):
    return regex.sub(pattern, RED + r"\g<0>" + NO_COLOR, text)


def find_in_po(pattern):
    table = []
    for file in glob("**/*.po"):
        pofile = polib.pofile(file)
        for entry in pofile:
            if entry.msgstr and regex.search(pattern, entry.msgid):
                table.append(
                    [
                        fill(entry.msgid, width=(WIDTH - 7) // 2),
                        fill(entry.msgstr, width=(WIDTH - 7) // 2),
                    ]
                )
    print(colorize(tabulate(table, tablefmt="fancy_grid"), pattern))


def parse_args():
    parser = argparse.ArgumentParser(description="Find translated words.")
    parser.add_argument("pattern")
    return parser.parse_args()


def main():
    args = parse_args()
    find_in_po(args.pattern)


if __name__ == "__main__":
    main()
