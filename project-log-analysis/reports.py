#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import cmd
import sys
import signal

DBNAME = "news"

MOST_POPULAR_ARTICLE_AUTHORS_QUERY = """
SELECT
  aad.name,
  sum(aad.access_count) as count
FROM
  (
    SELECT
      a.name,
      b.access_count
    FROM
      v_article_authors a
      INNER JOIN v_article_access_count b
      ON CONCAT('/article/', a.slug) = b.path
  ) AS aad
GROUP BY
  aad.name
ORDER BY
  count DESC;
"""

DAYS_WITH_MORE_THAN_N_PERCENT_ERROR_QUERY = """
SELECT
  *
FROM
  (
    SELECT
      to_char(v.date, 'Mon dd, yyyy') AS date,
      trunc(
        (cast(v.error_count as decimal) / v.total_count) * 100,
        2
      ) AS error_percentage
    FROM
      v_error_details_by_date v
  ) q3
WHERE
  q3.error_percentage > {}
ORDER BY q3.error_percentage DESC;
"""


class ArticlesReport():
    def __init__(self):
        self.db = psycopg2.connect(database=DBNAME)

    def n_most_popular_articles(self, n):
        c = self.db.cursor()
        query = """SELECT title, access_count
                        FROM v_articles_by_popularity
                        LIMIT {}
                """.format(n)
        c.execute(query)
        articles = c.fetchall()
        print("{} most popular article(s):\n".format(n))
        for a in articles:
            print('"{}" — {} views'.format(a[0], a[1]))
        print("\n")

    def most_popular_article_authors(self):
        query = MOST_POPULAR_ARTICLE_AUTHORS_QUERY
        c = self.db.cursor()
        c.execute(query)
        authors = c.fetchall()
        print("Most popular article author(s) of all time:\n")
        for a in authors:
            print('{} — {} views'.format(a[0], a[1]))
        print("\n")

    def days_with_more_than_n_percent_error(self, n):
        query = DAYS_WITH_MORE_THAN_N_PERCENT_ERROR_QUERY.format(n)
        c = self.db.cursor()
        c.execute(query)
        authors = c.fetchall()
        print("Days with more than {}% error requests:\n".format(n))
        for a in authors:
            print('{} — {}% errors'.format(a[0], a[1]))
        print("\n")

    def assignment_answers(self):
        self.n_most_popular_articles(3)
        self.most_popular_article_authors()
        self.days_with_more_than_n_percent_error(1)


class ArticlesReportCli(cmd.Cmd):
    intro = """
📒 Article Log Analysis Reports:

Enter relevant number applicable for your query
◽ For assignment answers:  1
-----
◽ For N most popular articles: 2 [ N=1 ]
◽ For Days with more than N% requests leading to errors: 3 [ N=1 ]
    """
    prompt = "> "

    def __init__(self):
        super(ArticlesReportCli, self).__init__()
        self.ar = ArticlesReport()

    def do_1(self, args):
        self.ar.assignment_answers()

    def do_2(self, args):
        n = args.split()[0] if args else 1
        try:
            n = int(n) if n else 1
        except ValueError:
            print("invalid argument, using default value 1 instead\n")
            n = 1
        self.ar.n_most_popular_articles(n)

    def do_3(self, args):
        n = args.split()[0] if args else 1
        try:
            n = float(n) if n else 1
        except ValueError:
            print("invalid argument, using default value 1 instead\n")
            n = 1
        self.ar.days_with_more_than_n_percent_error(n)

    def do_EOF(self, args):
        print('\n')
        return True


def handle_ctrl_c(signal, frame):
    print('\n')
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_ctrl_c)
    ar = ArticlesReportCli().cmdloop()
