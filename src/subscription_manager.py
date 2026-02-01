from database import get_session, User, ForcedChannel
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

class SubscriptionManager:
    
    @staticmethod
    async def check_subscription(user_id, bot, default_channel_id):
        """التحقق من اشتراك المستخدم في جميع القنوات المضافة"""
        import config
        
        # 1. استثناء المطور
        from admin_panel import AdminPanel
        if AdminPanel.is_admin(user_id):
            return True
            
        # 2. إذا كان الاشتراك الإجباري معطلاً
        if not getattr(config, 'ENABLE_FORCE_SUBSCRIBE', True):
            return True

        session = get_session()
        try:
            channels = session.query(ForcedChannel).all()
            
            # التحقق من القنوات المضافة في قاعدة البيانات
            for channel in channels:
                try:
                    member = await bot.get_chat_member(chat_id=channel.channel_id, user_id=user_id)
                    if member.status not in ['member', 'administrator', 'creator']:
                        return False
                except Exception as e:
                    logger.error(f"Error checking channel {channel.channel_id}: {e}")
                    continue

            # التحقق من القناة الافتراضية في config إذا كانت موجودة
            if default_channel_id:
                try:
                    member = await bot.get_chat_member(chat_id=default_channel_id, user_id=user_id)
                    if member.status not in ['member', 'administrator', 'creator']:
                        return False
                except Exception:
                    pass
            
            return True
        finally:
            session.close()
    
    @staticmethod
    def update_subscription_status(user_id, is_subscribed):
        """تحديث حالة الاشتراك في قاعدة البيانات"""
        session = get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                user.is_subscribed = is_subscribed
                session.commit()
        except Exception as e:
            logger.error(f"Database update failed: {e}")
        finally:
            session.close()
    
    @staticmethod
    def get_subscription_status(user_id):
        """الحصول على حالة اشتراك المستخدم من قاعدة البيانات"""
        session = get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            return user.is_subscribed if user else False
        finally:
            session.close()
    
    @staticmethod
    async def send_activation_notification(bot, activation_channel_id, user_id, username, country_name, phone_number, amount, activation_code='قيد الانتظار'):
        """إرسال إشعار التفعيل إلى قناة التفعيلات"""
        try:
            safe_username = username.replace("_", "\\_") if username else 'بدون معرف'
            me = await bot.get_me()
            bot_username = me.username
            
            message = (
                "تمت عملية الشراء 📰\n\n"
                f"• المستخدم : @{safe_username}\n"
                "• المنصة: تيليجرام\n"
                f"• الرقم: `{phone_number}`\n"
                f"• السعر: ${amount}\n"
                f"• الدوله : {country_name}\n"
                f"• معرف العميل: `{user_id}`\n"
                f"• كود التفعيل: `{activation_code}`\n"
                "• الحالة: تم التفعيل"
            )
            
            keyboard = [[InlineKeyboardButton("شـراء رقم 📞", url=f"https://t.me/{bot_username}?start=start")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await bot.send_message(
                chat_id=activation_channel_id, 
                text=message, 
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return True
        except Exception as e:
            logger.error(f"Activation notification failed: {e}")
            return False

class TwoStepVerification:
    @staticmethod
    def validate_2fa_code(code):
        clean_code = str(code).strip()
        return len(clean_code) >= 4 and clean_code.isdigit()
