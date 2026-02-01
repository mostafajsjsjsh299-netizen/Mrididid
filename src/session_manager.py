import re
import asyncio
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession

logger = logging.getLogger(__name__)

class SessionManager:
    @staticmethod
    def format_code_with_spaces(code):
        """تنسيق الكود بمسافات (مثال: 1 2 3 4 5)"""
        if not code:
            return ""
        clean_code = str(code).replace(" ", "").replace("-", "")
        return " ".join(clean_code)

    @staticmethod
    async def get_telegram_code(session_string, api_id, api_hash):
        """جلب الكود من رسائل تيليجرام الرسمية باستخدام Telethon"""
        client = None
        try:
            client = TelegramClient(StringSession(session_string), api_id, api_hash)
            await client.connect()
            
            if not await client.is_user_authorized():
                logger.error("Session is not authorized")
                return None
            
            code = None
            
            # Try to get messages from user 777 (Official Telegram)
            try:
                logger.info("Attempting to fetch code from ID 777")
                async for message in client.iter_messages(777, limit=10):
                    if message.text:
                        logger.info(f"Checking message from 777: {message.text[:50]}...")
                        # Search for 5-digit code
                        codes = re.findall(r'(?<!\d)(\d{5})(?!\d)', message.text)
                        if codes:
                            code = codes[0]
                            logger.info(f"Found code from 777: {code}")
                            break
            except Exception as e:
                logger.warning(f"Could not fetch by ID 777, trying search: {e}")
            
            if not code:
                # Fallback: Search for "Telegram" in dialogs to get the correct entity
                logger.info("Fallback: Searching dialogs for 'Telegram'")
                async for dialog in client.iter_dialogs(limit=20):
                    if dialog.name and ("Telegram" in dialog.name or dialog.id == 777):
                        logger.info(f"Found dialog: {dialog.name} (ID: {dialog.id})")
                        async for message in client.iter_messages(dialog.id, limit=10):
                            if message.text:
                                codes = re.findall(r'(?<!\d)(\d{5})(?!\d)', message.text)
                                if codes:
                                    code = codes[0]
                                    logger.info(f"Found code from dialog {dialog.name}: {code}")
                                    break
                        if code: break
            
            if not code:
                # Last resort: Scan all recent messages
                logger.info("Last resort: Scanning all recent messages")
                async for message in client.iter_messages(None, limit=20):
                    # Check if sender looks like Telegram
                    sender_name = ""
                    if message.sender:
                        sender_name = f"{getattr(message.sender, 'first_name', '')} {getattr(message.sender, 'last_name', '')}".strip()
                    
                    is_tg = False
                    if message.sender_id == 777: is_tg = True
                    elif message.sender and getattr(message.sender, 'username', '') == 'Telegram': is_tg = True
                    elif "Telegram" in sender_name: is_tg = True
                    
                    if is_tg and message.text:
                        logger.info(f"Found potential Telegram message from {sender_name}: {message.text[:50]}...")
                        codes = re.findall(r'(?<!\d)(\d{5})(?!\d)', message.text)
                        if codes:
                            code = codes[0]
                            logger.info(f"Found code from global scan: {code}")
                            break
            
            return code
        except Exception as e:
            logger.error(f"Error fetching code with Telethon: {e}")
            return None
        finally:
            if client:
                await client.disconnect()

    @staticmethod
    async def enable_2fa(session_string, api_id, api_hash, password="1212"):
        """تفعيل التحقق بخطوتين باستخدام Telethon"""
        client = None
        try:
            client = TelegramClient(StringSession(session_string), api_id, api_hash)
            await client.connect()
            
            if not await client.is_user_authorized():
                logger.error("Session is not authorized for 2FA")
                return False
            
            await client.edit_2fa(new_password=password)
            return True
        except Exception as e:
            logger.error(f"Error enabling 2FA with Telethon: {e}")
            return False
        finally:
            if client:
                await client.disconnect()
