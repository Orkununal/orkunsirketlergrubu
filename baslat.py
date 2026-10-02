"""Orkun SmartLead AI uygulamasını başlatır."""
import argparse
import secrets

from ayarlar import Config, environment_name
from uygulama import uygulama_olustur

# Render/Gunicorn import hedefi. Geliştirme için main() ayrı bir uygulama üretir.
uygulama = uygulama_olustur()
app = uygulama


def main():
    parser = argparse.ArgumentParser(description='Orkun SmartLead AI')
    parser.add_argument('--port', type=int, help='Yerel port (varsayılan: PORT veya 5000)')
    args = parser.parse_args()

    if args.port is not None and not 1 <= args.port <= 65535:
        parser.error('Port 1-65535 arasında olmalıdır.')

    overrides = {}
    generated_token = None
    if environment_name() == 'development' and not Config.ADMIN_API_TOKEN:
        generated_token = secrets.token_urlsafe(48)
        overrides['ADMIN_API_TOKEN'] = generated_token
    if args.port is not None:
        overrides['PORT'] = args.port

    application = uygulama_olustur(test_config=overrides)
    port = application.config['PORT']
    host = application.config['HOST']

    print(f'\nOrkun SmartLead AI: http://127.0.0.1:{port}', flush=True)
    print(f'Yönetim paneli: http://127.0.0.1:{port}/dashboard', flush=True)
    if generated_token:
        print('Bu çalıştırmaya ait geçici yönetici anahtarı:', flush=True)
        print(generated_token, flush=True)
    else:
        print('Yönetim için ayarladığınız ADMIN_API_TOKEN değerini kullanın.', flush=True)
    print('Durdurmak için Ctrl+C.\n', flush=True)

    application.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == '__main__':
    main()
