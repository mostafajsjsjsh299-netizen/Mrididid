from database import get_session, Country, PhoneNumber
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
import config
import asyncio

class CountryManager:
    @staticmethod
    def add_country(name, code, price):
        session = get_session()
        try:
            country = Country(name=name, code=code, price=price)
            session.add(country)
            session.commit()
            return True, country.id
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    @staticmethod
    def get_all_countries():
        session = get_session()
        try:
            return session.query(Country).filter_by(is_active=True).all()
        finally:
            session.close()

    @staticmethod
    def delete_country(country_id):
        session = get_session()
        try:
            country = session.query(Country).filter_by(id=country_id).first()
            if country:
                country.is_active = False
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()

class PhoneManager:
    @staticmethod
    def add_phone_to_db(country_id, phone_number, session_string, two_step_code="1212"):
        # لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
        session = get_session()
        try:
            phone = PhoneNumber(
                country_id=country_id,
                phone_number=phone_number,
                session_string=session_string,
                two_step_code=two_step_code
            )
            session.add(phone)
            session.commit()
            return True, "Success"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def get_available_phones(country_id):
        session = get_session()
        try:
            return session.query(PhoneNumber).filter_by(country_id=country_id, is_sold=False).all()
        finally:
            session.close()
    
    @staticmethod
    def sell_phone(phone_id, buyer_id):
        session = get_session()
        try:
            phone = session.query(PhoneNumber).filter_by(id=phone_id).first()
            if phone and not phone.is_sold:
                phone.is_sold = True
                phone.buyer_id = buyer_id
                phone.sold_at = datetime.now()
                session.commit()
                return True, phone
            return False, None
        finally:
            session.close()
