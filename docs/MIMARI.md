# Mimari ve dosya eşlemesi

Bu sürüm, tek dosyalı Orkun SmartLead AI projesini teknik rehberdeki **sorumlulukların ayrılığı** yaklaşımına göre modüllere böler.

```text
orkun_smartlead_ai_moduler/
├── baslat.py                     # Programı başlatır
├── ayarlar.py                    # Ortam ve uygulama ayarları
├── requirements.txt              # Standart paket listesi
├── gereksinimler.txt             # Rehberdeki Türkçe karşılık
├── .env.example                  # Gizli değerler için örnek
├── render.yaml                   # Render yayın ayarı
├── uygulama/
│   ├── __init__.py               # Uygulama fabrikası / montaj hattı
│   ├── database.py               # SQLite veri erişimi
│   ├── rotalar.py                # Sayfa ve API rotaları
│   ├── dogrulama.py              # Girdi doğrulama
│   ├── guvenlik.py               # Token kontrolü ve rate limit
│   ├── servisler/
│   │   └── yapay_zeka_servisi.py # Groq / demo AI servisi
│   ├── sablonlar/
│   │   ├── base.html
│   │   ├── index.html
│   │   └── dashboard.html
│   └── statik/
│       ├── style.css
│       ├── api.js
│       ├── index.js
│       └── dashboard.js
├── docs/
│   └── wix/                      # Wix Velo entegrasyon dosyaları
└── tests/
    └── test_smartlead.py
```

## Tek dosyadan yeni dosyalara eşleme

- `Config`, `DevelopmentConfig`, `ProductionConfig` -> `ayarlar.py`
- `get_db`, `init_db`, `lead_ekle`, `tum_leadler` -> `uygulama/database.py`
- `AIService` -> `uygulama/servisler/yapay_zeka_servisi.py`
- `ValidationError`, `validate_chat`, `validate_lead` -> `uygulama/dogrulama.py`
- `admin_authorized`, `RequestLimiter` -> `uygulama/guvenlik.py`
- Flask route fonksiyonları -> `uygulama/rotalar.py`
- `create_app` -> `uygulama/__init__.py` içinde `uygulama_olustur`
- Gömülü `TEMPLATES` -> `uygulama/sablonlar/`
- Gömülü `STATIC_FILES` -> `uygulama/statik/`

Ana işlev korunmuştur. Rehberle uyumluluk için `/panel`, `/saglik-durumu` ve `/api/adaylar` takma adresleri de eklenmiştir; mevcut `/dashboard`, `/health` ve `/api/leads` adresleri çalışmaya devam eder.
