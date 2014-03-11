#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-


from __future__ import with_statement
from glob import glob
import argparse, re, os, sys, sqlite3
from pymongo import MongoClient
from bs4 import BeautifulSoup

def main(args):
    """Loop thru all the games and parse them."""

    client = MongoClient()
    db     = client['jeopardy-database']
    gc     = db['jeopardy-games']

    if not os.path.isdir(args.dir):
        print "The specified folder is not a directory."
        sys.exit(1)
    NUMBER_OF_FILES = len(os.listdir(args.dir))
    if args.num_of_files:
        NUMBER_OF_FILES = args.num_of_files
    print "Parsing", NUMBER_OF_FILES, "files"
    if not args.stdout:
        pass
    for i, file_name in enumerate(glob(os.path.join(args.dir, "*.html")), 1):
        with open(os.path.abspath(file_name)) as f:
           print 'Printed game: ' + parse_game(f, gc, i)
    print "All done"

def parse_game(f, gc, gid):
    """Parses an entire Jeopardy! game and extract individual clues."""
    bsoup = BeautifulSoup(f, "lxml")

    game = {}
    game['id'] = gid
    game['categories'] = []

    # the title is in the format:
    # J! Archive - Show #XXXX, aired 2004-09-16
    # the last part is all that is required
    airdate = bsoup.title.get_text().split()[-1]
    game['airdate'] = airdate

    if not parse_round(bsoup, 1, game) or not parse_round(bsoup, 2, game):
        # one of the rounds does not exist
        pass
    # the final Jeopardy! round
    r = bsoup.find("table", class_ = "final_round")
    if not r:
        # this game does not have a final clue
        return "Invalid formatting or no final clue!"

    # Final Jeopardy Clue
    category = {}
    clue     = {}

    # Populate final jeopardy clue
    category['title'] = r.find("td", class_ = "category_name").get_text()
    category['round'] = 3
    category['clues'] = []
    clue['text']      = r.find("td", class_ = "clue_text").get_text()
    solution          = BeautifulSoup(r.find("div", onmouseover = True).get("onmouseover"), "lxml")
    solution          = solution.find("em").get_text()
    clue['solution']  = solution

    # Add final jeopardy clue to final jeopardy category
    category['clues'].append(clue)

    # Add final jeopardy category to game
    game['categories'].append(category)

    # Add Game to the database
    if not gc.find_one({'airdate': airdate}):
        game_id = str(gc.insert(game))
    else:
        game_id = "GAME ALREADY INSERTED"

    return game_id



def parse_round(bsoup, rnd, game):
    """Parses and inserts the list of clues from a whole round."""
    round_id = "jeopardy_round" if rnd == 1 else "double_jeopardy_round"
    r = bsoup.find(id = round_id)

    categories = []
    # the game may not have all the rounds
    if not r:
        return False
    # the list of categories for this round
    for c in r.find_all("td", class_ = "category_name"):
        category = {}
        category['title'] = c.get_text()
        category['clues'] = []
        categories.append(category)


    # the x_coord determines which category a clue is in
    # because the categories come before the clues, we will
    # have to match them up with the clues later on
    x = 0
    for a in r.find_all("td", class_ = "clue"):
        if not a.get_text().strip():
            continue
        value    = a.find("td", class_ = re.compile("clue_value")).get_text().lstrip("D: $")
        text     = a.find("td", class_ = "clue_text").get_text()
        solution = BeautifulSoup(a.find("div", onmouseover = True).get("onmouseover"), "lxml")
        solution = solution.find("em", class_ = "correct_response").get_text()

        # create clue
        clue = {}
        clue['value']    = value
        clue['text']     = text
        clue['solution'] = solution
        current_category = categories[x]
        current_category['clues'].append(clue)
        # always update x, even if we skip
        # a clue, as this keeps things in order. there
        # are 6 categories, so once we reach the end,
        # loop back to the beginning category
        #
        # x += 1
        # x %= 6
        x = 0 if x == 5 else x + 1

    # Add categories to game
    game['categories'] = categories

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Parse games from the J! Archive website.",
        add_help = False,
        usage = "%(prog)s [options]"
    )
    parser.add_argument(
        "-d", "--dir",
        dest = "dir",
        metavar = "<folder>",
        help = "the directory containing the game files",
        default = "j-archive"
    )
    parser.add_argument(
        "-n", "--number-of-files",
        dest = "num_of_files",
        metavar = "<number>",
        help = "the number of files to parse",
        type = int
    )
    parser.add_argument(
        "-f", "--filename",
        dest = "database",
        metavar = "<filename>",
        help = "the filename for the SQLite database",
        default = "clues.db"
    )
    parser.add_argument(
        "--stdout",
        help = "output the clues to stdout and not a database",
        action = "store_true"
    )
    parser.add_argument("--help", action = "help", help = "show this help message and exit")
    parser.add_argument("--version", action = "version", version = "2013.07.09")
    main(parser.parse_args())
