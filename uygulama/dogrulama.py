"""API giriş doğrulama yardımcıları."""
import re


class ValidationError(ValueError):
    pass


def text_field(data, key, minimum=1, maximum=2000):
    value = data.get(key, '')
    if not isinstance(value, str):
        raise ValidationError(f'{key} metin olmalıdır.')
    value = value.strip()
    if not minimum <= len(value) <= maximum:
        raise ValidationError(f'{key} alanı {minimum}-{maximum} karakter olmalıdır.')
    if any(ord(ch) < 32 and ch not in '\n\r\t' for ch in value):
        raise ValidationError(f'{key} geçersiz karakter içeriyor.')
    return value


def validate_chat(data, max_message, max_history):
    message = text_field(data, 'mesaj', maximum=max_message)
    history = data.get('gecmis', [])
    if not isinstance(history, list) or len(history) > max_history:
        raise ValidationError(f'gecmis en fazla {max_history} mesajlık bir liste olmalıdır.')
    cleaned = []
    for item in history:
        if not isinstance(item, dict) or item.get('role') not in ('user', 'assistant'):
            raise ValidationError('Geçmişte yalnızca user ve assistant rolleri kullanılabilir.')
        cleaned.append({'role': item['role'], 'content': text_field(item, 'content', maximum=max_message)})
    return message, cleaned


def validate_lead(data):
    name = text_field(data, 'isim', minimum=2, maximum=100)
    phone = text_field(data, 'telefon', maximum=30)
    message = text_field(data, 'mesaj', minimum=0, maximum=2000)
    if not re.fullmatch(r'\+?[0-9 ()\-]+', phone):
        raise ValidationError('Geçerli bir telefon numarası girin.')
    phone = re.sub(r'[ ()\-]', '', phone)
    if not 10 <= len(phone.lstrip('+')) <= 15:
        raise ValidationError('Telefon numarası 10-15 rakam içermelidir.')
    return name, phone, message
