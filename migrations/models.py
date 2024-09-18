from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from sqlalchemy.sql import func


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    message_part_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    conversation_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(String, nullable=False, index=True)
    author_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    message_part_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ChatbotPageUrls(Base):
    __tablename__ = "chatbot_page_urls"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(String, nullable=False, index=True)
    page_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
