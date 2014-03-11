Jeopardy parser for MongoDB
===========================

What is this?
-------------

Extracts [Jeopardy!] clues from the [J! Archive] website and dumps them into a MongoDB database for use elsewhere (no particular application is intended).

Python 2.7.5 and SQLite 3.7.12 are tested. Depends on BeautifulSoup 4 and the lxml parser.

Quick start
-----------
requires MongoDB, pymongo

```bash
pip install beautifulsoup4
pip install lxml
git clone git://github.com/whymarrh/jeopardy-parser.git
cd jeopardy-parser
python download.py
python parser.py
```

Thanks to [@knicholes](https://github.com/knicholes) for the Python download script.
Thanks to [@whymarr](https://github.com/whymarr) for the parser

How long will all this take?
----------------------------

The build script is doing two important things:

1. Downloading the game files from the J! Archive website
2. Parsing and inserting them into the database

The first part takes ~6.5 hours, the second part should take ~20 minutes (on a 1.7 GHz Core i5 w/ 4 GB RAM). Yes, that's a rather long time -- please submit a pull request if you can think of a way to shorten it. In total, running the build script will require ~7 hours.

As an aside: the complete download of the pages is ~350MB, and the resulting database file is ~20MB.

Querying the database
---------------------

The database is document based, and stores each game as its own document with an id and airdate as identifiers. Each game has three arrays of categories (one for each round), with each category consisting of a title and an array of each clue. The clues have text, solutions, and point values. 

License
-------

This software is released under the MIT License.

  [Jeopardy!]:http://www.jeopardy.com/
  [J! Archive]:http://j-archive.com/
  [1]:http://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx#naming_conventions
  [2]:https://github.com/whymarrh/jeopardy-parser/blob/master/parser.py#L49
