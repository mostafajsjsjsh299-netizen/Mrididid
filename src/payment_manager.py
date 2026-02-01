from database import get_session, User, Payment, Transaction
from datetime import datetime

class PaymentManager:
    @staticmethod
    def create_payment_request(user_id, amount, payment_method, screenshot_file_id):
        # لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
        session = get_session()
        try:
            payment = Payment(
                user_id=user_id,
                amount=amount,
                payment_method=payment_method,
                screenshot_file_id=screenshot_file_id,
                status="pending"
            )
            session.add(payment)
            session.commit()
            return payment.id
        except Exception as e:
            session.rollback()
            return None
        finally:
            session.close()
    
    @staticmethod
    def approve_payment(payment_id):
        # لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido
        session = get_session()
        try:
            payment = session.query(Payment).filter_by(id=payment_id).first()
            if payment and payment.status == "pending":
                payment.status = "completed"
                user = session.query(User).filter_by(user_id=payment.user_id).first()
                if user:
                    user.balance += payment.amount
                    transaction = Transaction(
                        user_id=payment.user_id,
                        amount=payment.amount,
                        transaction_type="charge"
                    )
                    session.add(transaction)
                    session.commit()
                    return True, user.balance
            return False, None
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    @staticmethod
    def reject_payment(payment_id):
        """لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido"""
        session = get_session()
        try:
            payment = session.query(Payment).filter_by(id=payment_id).first()
            if payment and payment.status == "pending":
                payment.status = "rejected"
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    @staticmethod
    def get_pending_payments():
        """لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido"""
        session = get_session()
        try:
            return session.query(Payment).filter_by(status="pending").all()
        finally:
            session.close()
    
    @staticmethod
    def charge_user_by_id(user_id, amount, admin_id):
        """لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido"""
        session = get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                user = User(user_id=user_id, balance=0.0)
                session.add(user)
            user.balance += amount
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                transaction_type="charge"
            )
            session.add(transaction)
            session.commit()
            return True, user.balance
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def withdraw_user_by_id(user_id, amount, admin_id):
        """لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido"""
        session = get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                return False, "المستخدم غير موجود"
            if user.balance < amount:
                return False, "رصيد المستخدم غير كافٍ لسحب هذا المبلغ"
            user.balance -= amount
            transaction = Transaction(
                user_id=user_id,
                amount=-amount,
                transaction_type="withdraw"
            )
            session.add(transaction)
            session.commit()
            return True, user.balance
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def transfer_balance(from_user_id, to_identifier, amount):
        """لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido"""
        session = get_session()
        try:
            from_user = session.query(User).filter_by(user_id=from_user_id).first()
            if not from_user or from_user.balance < amount:
                return False, "رصيدك غير كافٍ"
            
            if to_identifier.isdigit():
                to_user = session.query(User).filter_by(user_id=int(to_identifier)).first()
            else:
                to_user = session.query(User).filter_by(username=to_identifier.replace("@", "")).first()
                
            if not to_user:
                return False, "لم يتم العثور على المستلم"
                
            if from_user.user_id == to_user.user_id:
                return False, "لا يمكنك التحويل لنفسك"
                
            from_user.balance -= amount
            to_user.balance += amount
            
            t1 = Transaction(user_id=from_user.user_id, amount=-amount, transaction_type="transfer_out")
            t2 = Transaction(user_id=to_user.user_id, amount=amount, transaction_type="transfer_in")
            
            session.add_all([t1, t2])
            session.commit()
            return True, to_user.user_id
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

class BalanceManager:
    @staticmethod
    def get_user_balance(user_id):
        """الحصول على رصيد المستخدم"""
        session = get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            return user.balance if user else 0.0
        finally:
            session.close()
    
    @staticmethod
    def deduct_balance(user_id, amount):
        """خصم رصيد من المستخدم"""
        session = get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user and user.balance >= amount:
                user.balance -= amount
                transaction = Transaction(
                    user_id=user_id,
                    amount=-amount,
                    transaction_type="purchase"
                )
                session.add(transaction)
                session.commit()
                return True, user.balance
            return False, None
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def reset_all_balances():
        """لا يمسح بتعديل الملف ، الملف خاص بـ @Dev_Mido"""
        session = get_session()
        try:
            # تحديث جميع الأرصدة إلى 0
            session.query(User).update({User.balance: 0.0})
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()
