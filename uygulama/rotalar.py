"""Sayfa ve API rotaları."""
from flask import Blueprint, current_app, jsonify, render_template, request
from werkzeug.exceptions import BadRequest

from .database import lead_ekle, tum_leadler
from .dogrulama import ValidationError, validate_chat, validate_lead
from .guvenlik import admin_authorized
from .servisler.yapay_zeka_servisi import AIServiceError

pages = Blueprint('pages', __name__)
api = Blueprint('api', __name__)


def json_object():
    if not request.is_json:
        raise ValidationError('Content-Type application/json olmalıdır.')
    try:
        data = request.get_json()
    except BadRequest as exc:
        raise ValidationError('Geçerli bir JSON gövdesi gönderin.') from exc
    if not isinstance(data, dict):
        raise ValidationError('JSON gövdesi bir nesne olmalıdır.')
    return data


@pages.get('/')
def index():
    service = current_app.extensions['ai_service']
    return render_template('index.html', demo_mode=service.demo_mode)


@pages.get('/dashboard')
@pages.get('/panel')
def dashboard():
    return render_template('dashboard.html')


@api.before_request
def limit_requests():
    if request.method == 'OPTIONS':
        return None
    limiter = current_app.extensions['limiter']
    key = (request.remote_addr, request.endpoint)
    if not limiter.allowed(key, current_app.config['RATE_LIMIT_PER_MINUTE']):
        return jsonify(
            basari=False,
            hata='Çok sık istek gönderdiniz. Bir dakika sonra tekrar deneyin.'
        ), 429, {'Retry-After': '60'}


@api.post('/sohbet')
def sohbet():
    message, history = validate_chat(
        json_object(), current_app.config['MAX_MESSAGE_LENGTH'],
        current_app.config['MAX_HISTORY_MESSAGES']
    )
    service = current_app.extensions['ai_service']
    try:
        answer = service.yanit_uret(message, history)
        return jsonify(basari=True, cevap=answer, demo=service.demo_mode)
    except AIServiceError:
        current_app.logger.warning('AI servisi isteği başarısız oldu.')
        return jsonify(
            basari=False,
            hata='Asistan şu anda yanıt veremiyor. Lütfen tekrar deneyin veya teklif formunu kullanın.'
        ), 503


@api.post('/leads')
@api.post('/adaylar')
def lead_kaydet():
    name, phone, message = validate_lead(json_object())
    lead_id = lead_ekle(name, phone, message)
    return jsonify(basari=True, id=lead_id, mesaj='Görüşme talebiniz kaydedildi.'), 201


@api.get('/leads')
@api.get('/adaylar')
def lead_listele():
    if not admin_authorized():
        return jsonify(basari=False, hata='Yönetici erişim anahtarı gerekli veya hatalı.'), 401
    return jsonify(basari=True, leadler=tum_leadler())
