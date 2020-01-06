#!/usr/bin/env python
# coding: utf-8

import newscorpus.model as model
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///newscorpus.db')

print('Creating database tables from ORM classes.')

model.Base.metadata.create_all(engine)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

feed_paths = {
    'Health': 'health',
    'Lifestyle': 'section/lifestyle',
    'Opinion': 'opinion',
    'Politics': 'politics',
    'Science': 'science',
    'Sports': 'sports',
    'Tech': 'tech',
    'National': 'national',
    'World': 'world'
}

for k, v in feed_paths.items():
    print('Creating data feed record for {0}'.format(k))
    url = 'http://feeds.foxnews.com/foxnews/{0}'.format(v)

    data_feed = model.DataFeed(
        feed_name=k,
        feed_url=url
    )

    session.add(data_feed)

session.commit()

