from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_session, User, Country, PhoneNumber, Payment, BotSettings
from country_manager import CountryManager
from payment_manager import PaymentManager
import config

class AdminPanel:
    
    @staticmethod
    def is_admin(user_id):
        # لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
        return user_id == config.ADMIN_ID or user_id in getattr(config, 'SECONDARY_ADMIN_IDS', [])
    
    @staticmethod
    async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض لوحة تحكم المطور"""
        admin_ids = getattr(config, 'SECONDARY_ADMIN_IDS', [])
        secondary_admins = [aid for aid in admin_ids if aid != config.ADMIN_ID]
        admin_count = len(secondary_admins) + 1
        
        session = get_session()
        bot_status = session.query(BotSettings).filter_by(key='bot_status').first()
        status_text = "🟢 تشغيل" if bot_status and bot_status.value == 'off' else "🔴 إيقاف"
        session.close()

        keyboard = [
            [InlineKeyboardButton("➕ إضافة دولة", callback_data="admin_add_country"), InlineKeyboardButton("📱 إضافة رقم", callback_data="admin_add_phone")],
            [InlineKeyboardButton("💰 شحن مستخدم", callback_data="admin_charge_user"), InlineKeyboardButton("💸 سحب رصيد", callback_data="admin_withdraw_user")],
            [InlineKeyboardButton("🚫 حظر مستخدم", callback_data="admin_ban_user"), InlineKeyboardButton("✅ إلغاء حظر", callback_data="admin_unban_user")],
            [InlineKeyboardButton("📋 طلبات الدفع", callback_data="admin_pending_payments"), InlineKeyboardButton("🔧 إدارة الدول", callback_data="admin_manage_countries")],
            [InlineKeyboardButton("📢 إشتراك إجباري", callback_data="admin_manage_subs"), InlineKeyboardButton("🔔 قناة التفعيلات", callback_data="admin_manage_activation")],
            [InlineKeyboardButton("📝 تغيير الاقتباس", callback_data="admin_change_quote"), InlineKeyboardButton("📨 تغيير رسالة الترحيب", callback_data="admin_change_welcome")],
            [InlineKeyboardButton("💲 تغيير سعر دولة", callback_data="admin_change_price")],
            [InlineKeyboardButton("🎁 إنشاء هدية", callback_data="admin_create_gift"), InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_statistics")],
            [InlineKeyboardButton("⭐ تغيير سعر النجوم", callback_data="admin_change_stars_price"), InlineKeyboardButton(f"{status_text} البوت", callback_data="admin_toggle_bot")],
            [InlineKeyboardButton("🧹 تصفية جميع الأرصدة", callback_data="admin_confirm_reset_balances")],
            [InlineKeyboardButton(f"👥 إدارة الأدمنية ({admin_count})", callback_data="admin_manage_admins")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "🔧 **لوحة تحكم المطور**\n\nاختر العملية المطلوبة:"
        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            except Exception:
                if update.callback_query.message:
                    await update.callback_query.message.delete()
                    await update.callback_query.message.chat.send_message(text, reply_markup=reply_markup, parse_mode='Markdown')
        elif update.message:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    @staticmethod
    async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الإحصائيات"""
        session = get_session()
        try:
            total_users = session.query(User).count()
            
            # الحصول على التوب 7 (أكثر المستخدمين رصيداً أو نشاطاً - هنا سنفترض الرصيد أو إجمالي الشحن)
            # للتبسيط سنعرض التوب حسب الرصيد الحالي
            top_users = session.query(User).order_by(User.balance.desc()).limit(7).all()
            
            top_text = ""
            for i, user in enumerate(top_users, 1):
                username_display = str(user.username) if user.username else str(user.user_id)
                user_balance = float(user.balance) if user.balance is not None else 0.0
                top_text += f" │ {i}المسـتخدم  : @{username_display}\n"
                top_text += f" اشترك بـ : {user_balance} $\n"
            
            for i in range(len(top_users) + 1, 8):
                top_text += f" │ {i}المسـتخدم  : \n"
                top_text += f" اشترك بـ : $\n"

            text = f"▸ إجمالي الاعضاء : {total_users}\n" \
                   f"▸ التوب 7  بالبوت 👑 :\n" \
                   f" ┌────────────────┐\n" \
                   f"{top_text}" \
                   f" │المستخدمون الاخرون : \n" \
                   f"  └────────────────┘\n" \
                   f"▸ المطور والدعم : \n" \
                   f" 𓏺𝗠𝗮𝗳𝗶𝗮 - @cnrnrn\n" \
                   f" 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 - @vvcvcxr"
            
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]]
            try:
                if update.callback_query:
                    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                elif update.message:
                    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            except Exception as e:
                if update.callback_query and update.callback_query.message:
                    await update.callback_query.message.delete()
                    await update.callback_query.message.chat.send_message(text, reply_markup=InlineKeyboardMarkup(keyboard))
                elif update.message:
                    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        finally:
            session.close()
    
    @staticmethod
    async def show_pending_payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض طلبات الدفع المعلقة"""
        session = get_session()
        try:
            payments = session.query(Payment).filter_by(status='pending').all()
            if not payments:
                text = "✅ لا توجد طلبات دفع معلقة حالياً."
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]])
                try:
                    if update.callback_query:
                        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
                    elif update.message:
                        await update.message.reply_text(text, reply_markup=reply_markup)
                except Exception:
                    if update.callback_query and update.callback_query.message:
                        await update.callback_query.message.delete()
                        await update.callback_query.message.chat.send_message(text, reply_markup=reply_markup)
                return
            
            for p in payments:
                payment_id = str(p.id)
                user_id_val = str(p.user_id)
                amount_val = str(p.amount)
                method_val = str(p.payment_method)
                text = f"🆔 طلب #{payment_id}\n👤 المستخدم: `{user_id_val}`\n💰 المبلغ: `${amount_val}`\n💳 الطريقة: {method_val}"
                keyboard = [
                    [InlineKeyboardButton("✅ قبول", callback_data=f"approve_payment_{p.id}"),
                     InlineKeyboardButton("❌ رفض", callback_data=f"reject_payment_{p.id}")]
                ]
                try:
                    if update.effective_chat:
                        await context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=str(p.screenshot_file_id) if p.screenshot_file_id else "",
                            caption=text,
                            reply_markup=InlineKeyboardMarkup(keyboard),
                            parse_mode='Markdown'
                        )
                except:
                    if update.effective_chat:
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=text + "\n\n⚠️ (فشل تحميل الصورة)",
                            reply_markup=InlineKeyboardMarkup(keyboard),
                            parse_mode='Markdown'
                        )
        finally:
            session.close()
    
    @staticmethod
    async def manage_countries(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدارة الدول"""
        countries = CountryManager.get_all_countries()
        text = "🌍 **إدارة الدول:**\n\n"
        keyboard = []
        if countries:
            for country in countries:
                text += f"🆔 {country.id} | {country.name} ({country.code}) - ${country.price}\n"
                keyboard.append([InlineKeyboardButton(f"🗑️ حذف {country.name}", callback_data=f"delete_country_{country.id}")])
        keyboard.append([InlineKeyboardButton("➕ إضافة دولة جديدة", callback_data="admin_add_country")])
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")])
        try:
            if update.callback_query:
                await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            elif update.message:
                await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        except Exception:
            if update.callback_query and update.callback_query.message:
                await update.callback_query.message.delete()
                await update.callback_query.message.chat.send_message(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    @staticmethod
    async def manage_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدارة الأدمنية"""
        admin_ids = getattr(config, 'SECONDARY_ADMIN_IDS', [])
        main_admin = config.ADMIN_ID
        
        secondary_admins = [aid for aid in admin_ids if aid != main_admin]
        total_admins = len(secondary_admins) + 1
        
        text = f"👥 **إدارة الأدمنية**\n\n"
        text += f"📊 عدد الأدمنية: {total_admins}\n\n"
        text += f"👑 المطور الرئيسي: `{main_admin}`\n\n"
        
        if secondary_admins:
            text += "📋 الأدمنية الإضافيين:\n"
            for i, admin_id in enumerate(secondary_admins, 1):
                text += f"  {i}. `{admin_id}`\n"
        else:
            text += "📋 لا يوجد أدمنية إضافيين\n"
        
        keyboard = [
            [InlineKeyboardButton("➕ إضافة أدمن", callback_data="admin_add_admin")],
            [InlineKeyboardButton("➖ إزالة أدمن", callback_data="admin_remove_admin")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
        ]
        
        try:
            if update.callback_query:
                await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            elif update.message:
                await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        except Exception:
            if update.callback_query and update.callback_query.message:
                await update.callback_query.message.delete()
                await update.callback_query.message.chat.send_message(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    @staticmethod
    def add_admin(admin_id: int) -> bool:
        """إضافة أدمن جديد"""
        admin_ids = getattr(config, 'SECONDARY_ADMIN_IDS', [])
        if admin_id not in admin_ids:
            admin_ids.append(admin_id)
            config.SECONDARY_ADMIN_IDS = admin_ids
            AdminPanel._save_admins_to_file(admin_ids)
            return True
        return False
    
    @staticmethod
    def remove_admin(admin_id: int) -> bool:
        """إزالة أدمن"""
        admin_ids = getattr(config, 'SECONDARY_ADMIN_IDS', [])
        if admin_id in admin_ids and admin_id != config.ADMIN_ID:
            admin_ids.remove(admin_id)
            config.SECONDARY_ADMIN_IDS = admin_ids
            AdminPanel._save_admins_to_file(admin_ids)
            return True
        return False
    
    @staticmethod
    def _save_admins_to_file(admin_ids: list):
        """حفظ الأدمنية في الملف"""
        try:
            with open('sms_numbers_bot/config.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            new_content = re.sub(
                r'SECONDARY_ADMIN_IDS\s*=\s*\[.*?\]',
                f'SECONDARY_ADMIN_IDS = {admin_ids}',
                content
            )
            
            with open('sms_numbers_bot/config.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            print(f"Error saving admins: {e}")
