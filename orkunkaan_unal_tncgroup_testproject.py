import csv
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import orkunkaan_unal_tncgroup_51internationalprojecttrainingprogram_akillisatisdanismaniprojesi as project


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.settings = dict(TESTING=True, DATABASE_URL=str(Path(self.tmp.name) / 'test.db'),
                             ADMIN_API_TOKEN='test-admin-' + 'x' * 40, SECRET_KEY='x' * 48,
                             AI_PROVIDER='demo', GROQ_API_KEY='', RATE_LIMIT_PER_MINUTE=1000,
                             CORS_ORIGINS=['https://allowed.example'])
        self.app = project.create_app('development', self.settings)
        self.client = self.app.test_client()
        self.auth = {'Authorization': 'Bearer ' + self.settings['ADMIN_API_TOKEN']}
        self.lead = dict(isim='Demo Test', telefon='+90 555 000 00 00', mesaj='Ofis için hizmet talebi',
                         hizmet='Temizlik', tesis_turu='Ofis / İş merkezi',
                         konum='İstanbul / Kadıköy', baslangic='Bu ay')

    def create_lead(self, **changes):
        return self.client.post('/api/leads', json={**self.lead, **changes})

    def list_leads(self):
        response = self.client.get('/api/leads', headers=self.auth)
        self.assertEqual(response.status_code, 200)
        return response.json['leadler']

    def test_pages_and_guide_aliases(self):
        for url in ['/', '/panel', '/dashboard', '/health', '/saglik-durumu', '/static/index.js', '/static/dashboard.js', '/static/style.css']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        page = self.client.get('/').get_data(as_text=True)
        self.assertIn('Orkun Şirketler Grubu', page)
        self.assertIn('tesisInput', page)

    def test_structured_request_persists_and_defaults_to_new(self):
        response = self.create_lead()
        self.assertEqual(response.status_code, 201)
        row = self.list_leads()[0]
        for field in ['isim', 'mesaj', 'hizmet', 'tesis_turu', 'konum', 'baslangic']:
            self.assertEqual(row[field], self.lead[field])
        self.assertEqual(row['telefon'], '+905550000000')
        self.assertEqual(row['durum'], 'Yeni')
        self.assertTrue(row['tarih'].endswith('Z'))

    def test_guide_api_aliases_share_the_same_records(self):
        self.assertEqual(self.client.post('/api/adaylar', json=self.lead).status_code, 201)
        data = self.client.get('/api/adaylar', headers=self.auth).json
        self.assertEqual(data['toplam'], 1)
        self.assertEqual(data['adaylar'], self.list_leads())

    def test_old_form_contract_still_works(self):
        response = self.client.post('/api/leads', json={'isim': 'Demo Test', 'telefon': '05550000000'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.list_leads()[0]['hizmet'], '')

    def test_public_request_cannot_set_status(self):
        self.create_lead(durum='Kazanıldı')
        self.assertEqual(self.list_leads()[0]['durum'], 'Yeni')

    def test_admin_required_for_list_update_and_csv(self):
        for headers in [{}, {'Authorization': 'Bearer wrong'}]:
            for method, url in [('get', '/api/leads'), ('get', '/api/adaylar'), ('get', '/api/leads.csv'), ('patch', '/api/leads/1')]:
                with self.subTest(url=url, method=method):
                    self.assertEqual(getattr(self.client, method)(url, headers=headers).status_code, 401)

    def test_status_changes_persist_across_app_instances(self):
        lead_id = self.create_lead().json['id']
        for value in ['Görüşülüyor', 'Teklif iletildi', 'Kazanıldı', 'Kapandı', 'Yeni']:
            self.assertEqual(self.client.patch(f'/api/leads/{lead_id}', json={'durum': value}, headers=self.auth).status_code, 200)
            second = project.create_app('development', self.settings).test_client()
            self.assertEqual(second.get('/api/leads', headers=self.auth).json['leadler'][0]['durum'], value)

    def test_status_rejects_unknown_fields_and_values(self):
        lead_id = self.create_lead().json['id']
        for data in [{'durum': 'Unknown'}, {'durum': None}, {'durum': []}, {'durum': 'Yeni', 'isim': 'değiştir'}, {}]:
            self.assertEqual(self.client.patch(f'/api/leads/{lead_id}', json=data, headers=self.auth).status_code, 400)
        self.assertEqual(self.client.patch('/api/leads/999', json={'durum': 'Yeni'}, headers=self.auth).status_code, 404)

    def test_validation_does_not_create_partial_records(self):
        for data in [{'telefon': 'abc'}, {'isim': 'x'}, {'hizmet': 'Desteklenmeyen'}, {'tesis_turu': []}, {'baslangic': 'Dün'}, {'konum': 'x' * 121}, {'mesaj': 'x' * 2001}]:
            self.assertEqual(self.create_lead(**data).status_code, 400)
        self.assertEqual(self.list_leads(), [])

    def test_invalid_json_and_large_requests(self):
        self.assertEqual(self.client.post('/api/leads', data='x').status_code, 400)
        self.assertEqual(self.client.post('/api/leads', json=[]).status_code, 400)
        self.assertEqual(self.client.post('/api/leads', data='{', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post('/api/leads', data='x' * 70000, content_type='application/json').status_code, 413)

    def test_csv_roundtrip_and_formula_protection(self):
        self.create_lead(isim='=1+1', mesaj='satır 1; ayrım\nsatır 2', konum='@SUM(A1)')
        response = self.client.get('/api/leads.csv', headers=self.auth)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.startswith(b'\xef\xbb\xbf'))
        rows = list(csv.reader(io.StringIO(response.data.decode('utf-8-sig')), delimiter=';'))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][1], "'=1+1")
        self.assertEqual(rows[1][2], "'+905550000000")
        self.assertEqual(rows[1][5], "'@SUM(A1)")
        self.assertEqual(rows[1][8], 'satır 1; ayrım\nsatır 2')
        self.assertIn('attachment', response.headers['Content-Disposition'])

    def test_sql_like_text_is_only_data(self):
        self.create_lead(isim="Test'); DROP TABLE leads; --")
        self.create_lead()
        self.assertEqual(len(self.list_leads()), 2)

    def test_migration_preserves_old_records(self):
        path = Path(self.tmp.name) / 'legacy.db'
        with sqlite3.connect(path) as db:
            db.execute("CREATE TABLE leads (id INTEGER PRIMARY KEY, isim TEXT, telefon TEXT, mesaj TEXT, tarih TEXT)")
            db.execute("INSERT INTO leads VALUES (1, 'Eski Demo', '05550000000', 'Eski talep', '2026-09-01T00:00:00Z')")
        app = project.create_app('development', {**self.settings, 'DATABASE_URL': str(path)})
        migrated = app.test_client().get('/api/leads', headers=self.auth).json['leadler'][0]
        self.assertEqual(migrated['isim'], 'Eski Demo')
        self.assertEqual(migrated['mesaj'], 'Eski talep')
        self.assertEqual(migrated['durum'], 'Yeni')
        self.assertEqual(migrated['hizmet'], '')
        project.create_app('development', {**self.settings, 'DATABASE_URL': str(path)})

    def test_demo_answers_are_explicit_and_service_specific(self):
        with patch.object(project.requests, 'post') as remote:
            answers = []
            for service in self.app.config['SERVICES']:
                result = self.client.post('/api/sohbet', json={'mesaj': service}).json
                self.assertTrue(result['demo'])
                self.assertIn('hazır metin', result['cevap'])
                answers.append(result['cevap'])
            self.assertEqual(len(set(answers)), 4)
            remote.assert_not_called()

    def test_groq_contract_and_safe_failure(self):
        service = self.app.extensions['ai_service']
        service.settings.update(AI_PROVIDER='groq', GROQ_API_KEY='fake-key')
        response = Mock()
        response.json.return_value = {'choices': [{'message': {'content': 'Test yanıtı'}}]}
        with patch.object(project.requests, 'post', return_value=response) as remote:
            self.assertEqual(service.yanit_uret('Merhaba'), 'Test yanıtı')
            self.assertIn('Orkun Şirketler Grubu', remote.call_args.kwargs['json']['messages'][0]['content'])
        with patch.object(service, 'yanit_uret', side_effect=project.AIServiceError('secret')):
            response = self.client.post('/api/sohbet', json={'mesaj': 'Merhaba'})
            self.assertEqual(response.status_code, 503)
            self.assertNotIn('secret', response.get_data(as_text=True))

    def test_history_rejects_system_role(self):
        response = self.client.post('/api/sohbet', json={'mesaj': 'Merhaba', 'gecmis': [{'role': 'system', 'content': 'test'}]})
        self.assertEqual(response.status_code, 400)

    def test_rate_limit_and_alias_cannot_bypass_it(self):
        app = project.create_app('development', {**self.settings, 'RATE_LIMIT_PER_MINUTE': 1})
        client = app.test_client()
        self.assertEqual(client.post('/api/leads', json=self.lead).status_code, 201)
        response = client.post('/api/adaylar', json=self.lead)
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers['Retry-After'], '60')

    def test_cors_patch_and_security_headers(self):
        response = self.client.options('/api/leads/1', headers={'Origin': 'https://allowed.example', 'Access-Control-Request-Method': 'PATCH', 'Access-Control-Request-Headers': 'Authorization,Content-Type'})
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], 'https://allowed.example')
        self.assertIn('PATCH', response.headers['Access-Control-Allow-Methods'])
        bad = self.client.get('/api/leads', headers={**self.auth, 'Origin': 'https://other.example'})
        self.assertNotIn('Access-Control-Allow-Origin', bad.headers)
        self.assertEqual(bad.headers['Cache-Control'], 'no-store')
        self.assertIn("script-src 'self'", bad.headers['Content-Security-Policy'])

    def test_production_validates_configuration(self):
        for override in [{'SECRET_KEY': ''}, {'ADMIN_API_TOKEN': 'short'}, {'CORS_ORIGINS': ['*']}, {'AI_PROVIDER': 'unknown'}]:
            with self.assertRaises(ValueError):
                project.create_app('production', {**self.settings, **override})
        self.assertEqual(project.create_app('production', self.settings).test_client().get('/health').status_code, 200)

    def test_brand_is_configurable_and_html_is_escaped(self):
        app = project.create_app('development', {**self.settings, 'BRAND_NAME': '<b>Test Marka</b>', 'BRAND_TAGLINE': 'Özel slogan', 'ASSISTANT_NAME': 'Özel Asistan'})
        html = app.test_client().get('/').get_data(as_text=True)
        self.assertIn('&lt;b&gt;Test Marka&lt;/b&gt;', html)
        self.assertIn('Özel slogan', html)
        self.assertIn('Özel Asistan', html)
        self.assertNotIn(self.settings['ADMIN_API_TOKEN'], html)


if __name__ == '__main__':
    unittest.main()