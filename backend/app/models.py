# backend/app/models.py
# -*- coding: utf-8 -*-
"""SQLAlchemy модели — 12 таблиц"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# many-to-many users <-> roles
user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(120), unique=True, nullable=False)
    password = Column(String(256), nullable=False)  # простая строка в демо; в ВКР — хэшировать
    full_name = Column(String(200))
    email = Column(String(200), unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    roles = relationship('Role', secondary=user_roles, backref='users')

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    full_name = Column(String(200))
    email = Column(String(200), unique=True)
    phone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    group_id = Column(Integer, ForeignKey('groups.id'))

class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)

class Template(Base):
    __tablename__ = 'templates'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    subject = Column(String(300))
    body_html = Column(Text)
    creator_id = Column(Integer, ForeignKey('users.id'))

class Campaign(Base):
    __tablename__ = 'campaigns'
    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    template_id = Column(Integer, ForeignKey('templates.id'))
    creator_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_at = Column(DateTime, nullable=True)
    status = Column(String(50), default='draft')

class CampaignRecipient(Base):
    __tablename__ = 'campaign_recipients'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    client_id = Column(Integer, ForeignKey('clients.id'))
    status = Column(String(50), default='pending')

class Email(Base):
    __tablename__ = 'emails'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    subject = Column(String(500))
    body = Column(Text)
    status = Column(String(50), default='queued')
    sent_at = Column(DateTime, nullable=True)
    message_id = Column(String(200), nullable=True)

class Attachment(Base):
    __tablename__ = 'attachments'
    id = Column(Integer, primary_key=True)
    filename = Column(String(300))
    filepath = Column(String(500))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey('users.id'))

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    level = Column(String(20))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    key = Column(String(200), unique=True)
    value = Column(Text)
