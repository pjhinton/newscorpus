#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from newscorpus.feed_processing import retrieve_feeds, extract_items,\
    retrieve_articles


engine = create_engine('sqlite:///newscorpus.db')
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

retrieve_feeds(session)
extract_items(session)
retrieve_articles(session)
