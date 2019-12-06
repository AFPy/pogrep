#!/usr/bin/env python3
"""Find translations exemples by grepping in .po files.
"""

__version__ = "0.1.1"

import argparse
import curses
from glob import glob
import sys
from textwrap import fill

import regex
import polib
from tabulate import tabulate


def get_colors():
    """Just returns the CSI codes for red, green, magenta, and reset color.
    """
    try:
        curses.setupterm()
        fg_color = curses.tigetstr("setaf") or curses.tigetstr("setf") or ""
        red = str(curses.tparm(fg_color, 1), "ascii")
        green = str(curses.tparm(fg_color, 2), "ascii")
        magenta = str(curses.tparm(fg_color, 5), "ascii")
        no_color = str(curses.tigetstr("sgr0"), "ascii")
    except Exception:
        red, green, magenta = "", "", ""
        no_color = ""
    return red, green, magenta, no_color


RED, GREEN, MAGENTA, NO_COLOR = get_colors()


def get_term_width():
    scr = curses.initscr()
    width = scr.getmaxyx()[1]
    try:
        curses.endwin()
    except curses.error:
        pass
    return width


WIDTH = get_term_width()


def colorize(text, pattern, prefixes):
    result = regex.sub(pattern, RED + r"\g<0>" + NO_COLOR, text)
    for pnum, pfile in prefixes:
        if pfile:
            prefix = "( " + pfile + ")(" + pnum + ")"
            result = regex.sub(prefix, MAGENTA + r"\g<1>" + GREEN + r"\g<2>" + NO_COLOR, result)
        else:
            prefix = " " + pnum
            result = regex.sub(prefix, GREEN + r"\g<0>" + NO_COLOR, result)
    return result


def find_in_po(pattern, path, linenum, file_match):
    table = []
    prefixes = []
    for file in path[0]:
        try:
            pofile = polib.pofile(file.name)
        except OSError:
            print("{} doesn't seem to be a .po file".format(file), file=sys.stderr)
            continue
        for entry in pofile:
            if entry.msgstr and regex.search(pattern, entry.msgid):
                if file_match:
                    print(MAGENTA + file + NO_COLOR)
                    break
                left = entry.msgid
                if linenum:
                    pnum = str(entry.linenum) + ":"
                    if len(path[0]) > 1:
                        pfile = file + ":"
                    else:
                        pfile = ""
                    left = pfile + pnum + left
                    prefixes.append((pnum, pfile))
                table.append(
                    [
                        fill(left, width=(WIDTH - 7) // 2),
                        fill(entry.msgstr, width=(WIDTH - 7) // 2),
                    ]
                )
    if not file_match:
        print(colorize(tabulate(table, tablefmt="fancy_grid"), pattern, prefixes))


def parse_args():
    parser = argparse.ArgumentParser(description="Find translated words.")
    parser.add_argument("-i", "--ignore-case", action="store_true",
                        help="Ignore case distinctions, so that characters that differ only in case match each other.")
    parser.add_argument("-w", "--word-regexp", action="store_true",
                        help="Select only those lines containing matches that form whole words.")
    parser.add_argument('-n', "--line-number", action="store_true",
                        help="Prefix each line of output with the 1-based line number within its input file.")
    parser.add_argument("-l", "--files-with-matches", action="store_true",
                        help="Suppress normal output; instead print the name of each input file from which output "
                             "would normally have been printed.  The scanning will stop on the first match.")
    parser.add_argument("pattern")
    parser.add_argument("path", action="append", type=argparse.FileType('r'), nargs='+')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.word_regexp:
        args.pattern = r"\b" + args.pattern + r"\b"
    if args.ignore_case:
        args.pattern = r"(?i)" + args.pattern
    find_in_po(args.pattern, args.path, args.line_number, args.files_with_matches)


if __name__ == "__main__":
    main()
