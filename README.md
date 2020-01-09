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

## Common Parameters

The scripts in this package take two positional arguments:

* `logdir` - The full path to a directory where log files should be written.
* `dbconn` - The [SQLAlchemy database URL](https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls) where data will be written to

## Corpus Storage and Setup

All data is persisted in a database, which is managed and accessed via
the SQLAlchemy ORM API.  Table creation and feed URL population is accomplished
via the `nc_setup_db` script.  

## Retrieving Data for Corpus

The `nc_process_feeds` script polls all feeds and processes articles not currently
stored in the database.  The final product is a plain text version of the article 
content as well as article metadata.  This script should be invoked at regular 
intervals by your favorite job scheduler.

## Corpus Creation and Data Model

Each poll attempt is stored in the `feed_retrievals` table and includes a copy
of the raw RSS XML and data about the HTTP request itself.

Each RSS XML item is processed for article metadata and the URL for retrieving
the article's webpage.  This data is stored in the `feed_items` table.

Each RSS items may include one or more category elements with a domain attribute
of `foxnews.com/taxonomy`.  Each distinct category is stored in a `categories` table, 
and associations with articles is accomplished via a many-to-many mapping table.

Each article webpage is retrieved via HTTP. The HTML response is retained, and
the content of the article is isolated as plain text, sans teaser hyperlinks.
All of this data and the HTTP request metadata are stored in the 
`article_retrievals` table.

## Future Work

Plans are to refine this package to support articles published previously and
available via the websites `sitemap.xml` file.

Provide greater flexibility beyond just required command line arguments to specify
the log file directory and database connection.  Most likely this will involve
a configuration file and environment variables.

## About the Name

The name of the package is a portmanteau derived from fusing the former parent 
of Fox News (News Corp) with the word "corpus".
