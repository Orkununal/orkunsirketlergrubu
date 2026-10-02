# Orkun SmartLead AI - Modüler Sürüm

Tek Python dosyası hâlindeki proje, teknik rehberdeki klasör yaklaşımına göre ayrıştırılmıştır. Arayüz, SQLite kayıtları, Groq/demo yapay zekâ akışı, yönetici tokenı, CORS, rate limit ve güvenlik başlıkları korunmuştur.

## Kurulum

Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

CMD:

```bat
venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

## Ortam ayarları

`.env.example` dosyasını `.env` adıyla kopyalayın. Gerçek API anahtarını yalnızca kendi `.env` dosyanıza yazın; `.env` Git'e gönderilmez.

AI anahtarı girmezseniz uygulama **demo modu** ile açılır. Geliştirme ortamında `ADMIN_API_TOKEN` boşsa `python baslat.py` komutu o çalıştırma için geçici bir yönetici anahtarı üretip terminalde gösterir.

## Çalıştırma

```powershell
python baslat.py
```

Adresler:

- Ana sayfa: `http://127.0.0.1:5000/`
- Yönetim paneli: `http://127.0.0.1:5000/dashboard`
- Sağlık kontrolü: `http://127.0.0.1:5000/health`
- Sohbet API: `POST /api/sohbet`
- Lead ekleme: `POST /api/leads`
- Lead listeleme: `GET /api/leads` + `Authorization: Bearer <ADMIN_API_TOKEN>`

Rehberdeki adlara yakın takma yollar da vardır: `/panel`, `/saglik-durumu`, `/api/adaylar`.

## Test

```powershell
python -m unittest discover -s tests -v
```

## Klasör yapısı

Ayrıntılı eşleme için `docs/MIMARI.md` dosyasına bakın.

## Render

`render.yaml` modüler sürüme göre güncellenmiştir. Başlatma hedefi `baslat:uygulama`dır. Üretimde `SECRET_KEY`, `ADMIN_API_TOKEN`, `GROQ_API_KEY` ve gerçek `CORS_ORIGINS` değerlerini Render Environment bölümünden tanımlayın.

## Wix

Wix Velo örnekleri `docs/wix/` altındadır. `API_BASE` değerini yayınladığınız backend adresiyle değiştirin.
