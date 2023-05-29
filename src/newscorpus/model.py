from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class DataFeed(Base):
    __tablename__ = "data_feeds"

    id = Column(Integer, primary_key=True)
    feed_name = Column(String(16), nullable=False, unique=True)
    feed_url = Column(String(512), nullable=False, unique=True)

    retrievals = relationship("FeedRetrieval", back_populates="data_feed")

    def __repr__(self):
        return '<DataFeed id="{0}" feed_name="{1}">'.format(self.id, self.feed_name)


class FeedRetrieval(Base):
    __tablename__ = "feed_retrievals"

    id = Column(Integer, primary_key=True)
    data_feed_id = Column(Integer, ForeignKey("data_feeds.id"))
    http_status = Column(Integer)
    http_reason = Column(String(256))
    retrieved_on = Column(DateTime(timezone=True))
    feed_content = Column(Text)
    needs_processing = Column(Boolean, nullable=False, default=True)

    data_feed = relationship("DataFeed", back_populates="retrievals")

    items = relationship("FeedItem", back_populates="feed_retrieval")

    def __repr__(self):
        return (
            '<FeedRetrieval id="{0}" data_feed_id="{1}" '
            + 'retrieved_on="{2}" needs_processing="{3}">'.format(
                self.id, self.data_feed_id, self.retrieved_on, self.needs_processing
            )
        )


class FeedItem(Base):
    __tablename__ = "feed_items"

    id = Column(Integer, primary_key=True)
    feed_retrieval_id = Column(Integer, ForeignKey("feed_retrievals.id"))
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    source = Column(String(256), nullable=False)
    creator = Column(Text)
    published_on = Column(DateTime, nullable=False)
    url = Column(String(256), nullable=False)
    needs_processing = Column(Boolean, nullable=False, default=True)

    feed_retrieval = relationship("FeedRetrieval", back_populates="items")

    article_retrievals = relationship("ArticleRetrieval", back_populates="feed_item")

    categories = relationship(
        "Category", secondary="item_categories", back_populates="items"
    )

    def __repr__(self):
        return '<FeedItem id="{0}" title="{1}" needs_processing="{2}">'.format(
            self.id, self.title, self.needs_processing
        )


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    category = Column(String(256), unique=True)

    items = relationship(
        "FeedItem", secondary="item_categories", back_populates="categories"
    )

    def __repr__(self):
        return '<Category id="{0}" category="{1}">'.format(self.id, self.category)


item_categories = Table(
    "item_categories",
    Base.metadata,
    Column("feed_item_id", ForeignKey("feed_items.id"), primary_key=True),
    Column("category_id", ForeignKey("categories.id"), primary_key=True),
)


class ArticleRetrieval(Base):
    __tablename__ = "article_retrievals"
    id = Column(Integer, primary_key=True)
    feed_item_id = Column(Integer, ForeignKey("feed_items.id"))
    http_status = Column(Integer)
    http_reason = Column(String(256))
    html_source = Column(Text, nullable=False)
    extracted_text = Column(Text)
    retrieved_on = Column(DateTime, nullable=False)

    feed_item = relationship("FeedItem", back_populates="article_retrievals")

    def __repr__(self):
        return '<ArticleRetrieval id="{0}" retrieved_on="{1}>'.format(
            self.id, self.retrieved_on
        )
