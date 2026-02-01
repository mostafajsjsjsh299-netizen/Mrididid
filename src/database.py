from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Gift(Base):
    __tablename__ = 'gifts'
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    amount = Column(Float)
    max_uses = Column(Integer)
    current_uses = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(Integer)

class ForcedChannel(Base):
    __tablename__ = 'forced_channels'
    id = Column(Integer, primary_key=True)
    channel_id = Column(String, unique=True) # e.g. @channel or -100...
    link = Column(String)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    balance = Column(Float, default=0.0)
    is_banned = Column(Boolean, default=False)
    is_subscribed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

class BotSettings(Base):
    __tablename__ = 'bot_settings'
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    value = Column(Text)

class Country(Base):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)

class PhoneNumber(Base):
    __tablename__ = 'phone_numbers'
    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, nullable=False)
    phone_number = Column(String, nullable=False)
    session_string = Column(Text, nullable=True)
    two_step_code = Column(String, default="1212")
    is_sold = Column(Boolean, default=False)
    buyer_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    sold_at = Column(DateTime, nullable=True)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)
    screenshot_file_id = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.now)

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
engine = create_engine('sqlite:///bot_database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_session():
    return Session()
