import datetime
import logging
import xml.etree.ElementTree as ET

import requests

from bs4 import BeautifulSoup
from sqlalchemy import and_
from newscorpus.model import DataFeed, FeedRetrieval, FeedItem,\
    ArticleRetrieval, Category


def get_url(url):
    r = requests.get(url)
    return r.text, r.status_code, r.reason


def process_feed_xml(feed_xml):
    
    result = []
    
    elroot = ET.fromstring(feed_xml)

    items = elroot.findall('.//item')

    for item in items:
        resdict = {}
        
        link = item.find('./link')
        permalink = item.find('./guid[@isPermaLink="true"]')
        title = item.find('./title')
        description = item.find('./description')
        pubdate = item.find('./pubDate')
        source = item.find('./category[@domain="foxnews.com/metadata/dc.source"]')
        creator = item.find('./category[@domain="foxnews.com/metadata/dc.creator"]')
        taxcats = item.findall('./category[@domain="foxnews.com/taxonomy"]')
        
        taxonomy = []   
        for taxcat in taxcats:
            taxonomy.append(taxcat.text)
        resdict['taxonomy'] = taxonomy

        resdict['source'] = source.text

        resdict['title'] = title.text
        resdict['description'] = description.text
        resdict['pubdate'] = pubdate.text

        if creator is not None:
            resdict['creator'] = creator.text

        if permalink is not None:
            resdict['permalink'] = permalink.text
        else:
            resdict['permalink'] = link.text
            
        result.append(resdict)
    
    return result


def extract_text(article_html):
    soup = BeautifulSoup(article_html, 'html.parser')
    res = soup.find('div', class_='article-body')
    
    if res is not None:
        article_text = ''
        for it in res:
            if it.name == 'p':
                p_text = it.get_text()
                # ignore teaser links
                if p_text != p_text.upper():
                    article_text += (p_text + '\n')
    else:
        article_text = None

    return article_text


def retrieve_feeds(session):
    
    feeds = session.query(DataFeed).all()

    for f in feeds:
        try:
            (feed_content, http_status, http_reason) = get_url(f.feed_url)
        except Exception as ex:
            print(ex)
            continue
        retrieved_on = datetime.datetime.now()
        feed_retrieval = FeedRetrieval(
            data_feed_id=f.id,
            feed_content=feed_content,
            http_status=http_status,
            http_reason=http_reason,
            needs_processing=(http_status==200), # Don't try to process if HTTP request error
            retrieved_on=retrieved_on
        )
        session.add(feed_retrieval)
        logging.info('Created: {0}'.format(feed_retrieval))

    session.commit()


def extract_items(session):

    feed_retrievals = session.query(FeedRetrieval).filter_by(needs_processing=True)

    all_items = []
    feed_retrieval_map = {}
    feed_categories = set()
    db_category_map = {}
    feed_item_counts = {}

    for f in feed_retrievals:
        items = process_feed_xml(f.feed_content)
        for itm in items:
            # Use the feed item's URL as a key
            # so that we can determine what feed
            # retieval was associated with this item.
            feed_retrieval_map[itm['permalink']] = f.id
            if f.id not in feed_item_counts:
                feed_item_counts[f.id] = 1
            else:
                feed_item_counts[f.id] += 1
            # accumulate all taxonomy topics for items in
            # feed and get their IDs with a single query
            for t in itm['taxonomy']:
                feed_categories.add(t)
        all_items += items

    # Retrieve Category objects for all categories
    # that currently exist in the database.
    db_categories = session.query(Category).filter(
            Category.category.in_(list(feed_categories))
    ).all()

    db_category_map = {c.category: c for c in db_categories}

    db_categories = set(db_category_map.keys())

    # Determine what category records need to be 
    # created anew.
    new_categories = feed_categories.difference(db_categories)

    for nc in new_categories:
        category = Category(category=nc)
        session.add(category)
        logging.info('Created: {0}'.format(category))
        session.commit()
        db_category_map[nc] = category

    for itm in all_items:

        # convert RSS feed timestamp into SQL DATETIME
        published_on = datetime.datetime.strptime(
            itm['pubdate'],
            '%a, %d %b %Y %H:%M:%S %Z'
        )

        feed_retrieval_id = feed_retrieval_map[itm['permalink']]

        # skip over any items that have been 
        # already added because they were seen
        # during previous feed processings
        item_count = session.query(FeedItem).filter(
            and_(
               FeedItem.url == itm['permalink'],
               FeedItem.published_on == published_on
            )
        ).count()
        if item_count > 0:
            feed_item_counts[feed_retrieval_id] -= 1
            continue

        feed_item = FeedItem(
            feed_retrieval_id=feed_retrieval_id,
            title=itm['title'],
            description=itm['description'],
            source=itm['source'],
            published_on=published_on,
            creator=itm.get('creator', None),
            url=itm['permalink']
        )

        for c in itm['taxonomy']:
            feed_item.categories.append(db_category_map[c])

        session.add(feed_item)

        logging.info('Created: {0}'.format(feed_item))

        feed_item_counts[feed_retrieval_id] -= 1

        if feed_item_counts[feed_retrieval_id] == 0:
            feed_retrieval = session.query(FeedRetrieval).filter_by(
                id=feed_retrieval_id
            ).one()
            feed_retrieval.needs_processing = False
            session.add(feed_retrieval)
    
        session.commit()


def retrieve_articles(session):

    feed_items = session.query(FeedItem).\
        filter_by(needs_processing=True).all()

    for fi in feed_items:

        (article_html, http_status, http_reason) = get_url(fi.url)

        retrieved_on = datetime.datetime.now()
        extracted_text = extract_text(article_html)

        article_retrieval = ArticleRetrieval(
            feed_item_id=fi.id,
            http_status=http_status,
            http_reason=http_reason,
            html_source=article_html,
            extracted_text=extracted_text,
            retrieved_on=retrieved_on
        )
        session.add(article_retrieval)

        logging.info('Created: {0}'.format(article_retrieval))

        fi.needs_processing=False
        session.add(fi)
        
    session.commit()
