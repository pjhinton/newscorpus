# newscorpus

Builds a SQLite database for a text corpus of Fox News Channel website articles.

This package was created to facilitate research into content published on the 
Fox New Channel website. (https://www.foxnews.com/).  It is the hope of this 
package's developer that this code will encourage research into Fox News 
[epistemic closure](http://www.juliansanchez.com/2010/03/26/frum-cocktail-parties-and-the-threat-of-doubt/).

Content is discovered by retrieving and processing FeedBurner hosted RSS feeds.

* Health (20 most recent articles)
* Lifestyle (10 most recent articles)
* National (20 most recent articles)
* Opinion (20 most recent articles)
* Politics (10 most recent articles)
* Science (10 most recent articles)
* Sports (20 most recent articles)
* Tech (10 most recent articles)
* World (20 most recent articles)

The Latest and Most Popular feeds are ignored because their items overlap 
with the others.  The Video feed is ignored because the focus of this project
is textual content.  The Travel feed is ignored because the URL provided on 
their [feed listing](https://www.foxnews.com/about/rss/) site is not accessible.

## Corpus Storage and Setup

All data is persisted in an SQLite database, which is managed and accessed via
the SQLAlchemy ORM API.  Table creation and feed URL population is accomplished
fia the `setup_db.py` script.  The database file is created in the current
working directory of the invoking shell.

## Retrieving Data for Corpus

The `process_feeds.py` script polls all feeds and processes articles not currently
stored in the database.  The final product is a plain text version of the article 
content as well as article metadata.  This script should be invoked in the same
directory where the corpus database file resides at regular intervals by your
favorite job scheduler.

## Corpus Creation and Data Model

Each poll attempt is stored in the `feed_retrievals` table and includes a copy
of the raw RSS XML and data about the HTTP request itself.

Each feed item is processed for article metadata and the URL for retrieving
the article's webpage.  This data is stored in the `feed_items` table.

Categories associated with each article are stored in a `categories` table, 
and associations with articles is accomplished via a many-to-many mapping table.

Each article webpage is retrieved via HTTP. The HTML response is retained, and
the content of the article is isolated as plain text, sans teaser hyperlinks.
All of this data and the HTTP request metadata are stored in the 
`article_retrievals` table.

## Future Work

Plans are to refine this package to support articles published previously and
available via the websites `sitemap.xml` file.

Work will be done to make the configuration more flexible, like supporting
databases beyond SQLite.

The name of the package is a portmanteau derived from fusing the former parent 
of Fox News (News Corp) with the word "corpus".
