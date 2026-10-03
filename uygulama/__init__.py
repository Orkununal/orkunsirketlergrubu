"""SmartLead AI uygulama fabrikası."""
import secrets
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from ayarlar import config_by_name, environment_name
from .database import DatabaseError, init_db
from .dogrulama import ValidationError
from .guvenlik import RequestLimiter
from .servisler.yapay_zeka_servisi import AIService


def uygulama_olustur(ayar_adi=None, test_config=None):
    name = ayar_adi or environment_name()
    if name not in config_by_name:
        raise ValueError('APP_ENV development veya production olmalıdır.')

    app = Flask(
        __name__, template_folder='sablonlar', static_folder='statik', static_url_path='/static'
    )
    app.config.from_object(config_by_name[name])
    if test_config:
        app.config.update(test_config)

    if name == 'production':
        if len(app.config['SECRET_KEY']) < 32 or len(app.config['ADMIN_API_TOKEN']) < 32:
            raise ValueError('Üretimde SECRET_KEY ve ADMIN_API_TOKEN en az 32 karakter olmalıdır.')
    else:
        app.config['SECRET_KEY'] = app.config['SECRET_KEY'] or secrets.token_hex(32)

    if app.config['AI_PROVIDER'] not in ('groq', 'demo'):
        raise ValueError('AI_PROVIDER groq veya demo olmalıdır.')

    app.json.ensure_ascii = False
    CORS(app)

    with app.app_context():
        init_db(app)

    app.extensions['ai_service'] = AIService(dict(app.config))
    app.extensions['limiter'] = RequestLimiter()

    from .rotalar import api, pages
    app.register_blueprint(pages)
    app.register_blueprint(api, url_prefix='/api')

    @app.get('/health')
    @app.get('/saglik-durumu')
    def health():
        return jsonify(basari=True, durum='aktif')

    @app.errorhandler(ValidationError)
    def validation_error(error):
        return jsonify(basari=False, hata=str(error)), 400

    @app.errorhandler(DatabaseError)
    def database_error(_error):
        app.logger.warning('Veritabanı işlemi başarısız oldu.')
        return jsonify(
            basari=False,
            hata='Veri hizmeti şu anda kullanılamıyor. Lütfen tekrar deneyin.'
        ), 503

    @app.errorhandler(HTTPException)
    def http_error(error):
        response = error.get_response()
        response.data = app.json.dumps({'basari': False, 'hata': {
            404: 'Adres bulunamadı.', 405: 'Bu işlem desteklenmiyor.',
            413: 'İstek boyutu çok büyük.'
        }.get(error.code, 'İstek işlenemedi.')})
        response.content_type = 'application/json'
        return response

    @app.errorhandler(Exception)
    def unexpected_error(error):
        app.logger.error('Beklenmeyen hata: %s', type(error).__name__)
        return jsonify(
            basari=False,
            hata='Beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.'
        ), 500

    @app.after_request
    def response_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; "
            "base-uri 'self'; form-action 'self'"
        )
        if request.path.startswith('/api/') or request.path in ('/dashboard', '/panel'):
            response.headers['Cache-Control'] = 'no-store'
        return response

    return app


create_app = uygulama_olustur
