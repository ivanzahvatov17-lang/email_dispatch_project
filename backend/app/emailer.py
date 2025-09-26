# backend/app/emailer.py
# -*- coding: utf-8 -*-
"""
Модуль отправки писем через SMTP.
Комментарии на русском. Лёгкая, безопасная реализация без внешних платных сервисов.
"""

from email.message import EmailMessage
import smtplib
import ssl
from datetime import datetime
from typing import List, Optional
from .db import SessionLocal
from . import models

def _get_setting(sess, key: str) -> Optional[str]:
    """Вернуть значение настройки из таблицы settings по ключу."""
    s = sess.query(models.Setting).filter(models.Setting.key == key).first()
    return s.value if s else None

def send_email_smtp(to_email: str, subject: str, body_html: str, attachments: Optional[List[str]] = None) -> Optional[str]:
    """
    Отправляет одно письмо через SMTP.
    Возвращает message_id (внутренний) при успехе, иначе None.
    Логирование сохраняется в таблице Log и Email.
    """
    sess = SessionLocal()
    try:
        # Загружаем параметры SMTP из таблицы settings
        host = _get_setting(sess, 'smtp_host') or 'localhost'
        port = int(_get_setting(sess, 'smtp_port') or 25)
        user = _get_setting(sess, 'smtp_user') or ''
        password = _get_setting(sess, 'smtp_pass') or ''
        default_from = _get_setting(sess, 'smtp_from') or (user or f'noreply@{host}')

        msg = EmailMessage()
        msg['From'] = default_from
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.set_content("Это письмо в формате HTML. Если вы видите этот текст — ваш клиент не поддерживает HTML.")
        msg.add_alternative(body_html, subtype='html')

        # Вложенные файлы (опционально)
        if attachments:
            for path in attachments:
                try:
                    with open(path, 'rb') as f:
                        data = f.read()
                        filename = path.split('/')[-1].split('\\')[-1]
                        msg.add_attachment(data, maintype='application', subtype='octet-stream', filename=filename)
                except Exception as e:
                    # записываем лог, но не прерываем отправку
                    sess.add(models.Log(level='ERROR', message=f'Attachment read error: {e} ({path})'))
                    sess.commit()

        # Отправка
        try:
            # Для TLS (обычно порт 587)
            context = ssl.create_default_context()
            if port in (465,):  # SMTPS
                with smtplib.SMTP_SSL(host, port, context=context) as server:
                    if user and password:
                        server.login(user, password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(host, port, timeout=30) as server:
                    # Если сервер поддерживает STARTTLS и мы работаем на стандартном порту
                    try:
                        server.starttls(context=context)
                    except Exception:
                        # некоторые локальные debug-серверы не поддерживают starttls — игнорируем
                        pass
                    if user and password:
                        server.login(user, password)
                    server.send_message(msg)

            message_id = f"{int(datetime.utcnow().timestamp())}-{to_email}"
            # Логируем отправку в Email и Log
            email_record = models.Email(
                campaign_id=None,
                client_id=None,
                subject=subject,
                body=body_html,
                status='sent',
                sent_at=datetime.utcnow(),
                message_id=message_id
            )
            sess.add(email_record)
            sess.add(models.Log(level='INFO', message=f'Email sent to {to_email}, message_id={message_id}'))
            sess.commit()
            return message_id
        except Exception as send_exc:
            sess.add(models.Log(level='ERROR', message=f'Email send failed to {to_email}: {send_exc}'))
            sess.commit()
            return None
    finally:
        sess.close()
