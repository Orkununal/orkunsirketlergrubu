import tempfile
import unittest
from pathlib import Path

from uygulama import uygulama_olustur
from uygulama.dogrulama import ValidationError, validate_lead
from uygulama.guvenlik import RequestLimiter


class SmartLeadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        db = str(Path(self.tmp.name) / 'test.db')
        self.token = 'test-token-1234567890-test-token-1234567890'
        self.app = uygulama_olustur(test_config={
            'TESTING': True,
            'DATABASE_URL': db,
            'AI_PROVIDER': 'demo',
            'GROQ_API_KEY': '',
            'ADMIN_API_TOKEN': self.token,
            'CORS_ORIGINS': ['http://localhost:5000'],
            'RATE_LIMIT_PER_MINUTE': 1000,
        })
        self.client = self.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def test_health(self):
        self.assertEqual(self.client.get('/health').status_code, 200)
        self.assertEqual(self.client.get('/saglik-durumu').status_code, 200)

    def test_pages(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/dashboard').status_code, 200)
        self.assertEqual(self.client.get('/panel').status_code, 200)

    def test_demo_chat(self):
        response = self.client.post('/api/sohbet', json={'mesaj': 'Temizlik hizmeti hakkında bilgi.'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['demo'])

    def test_lead_create_and_list(self):
        created = self.client.post('/api/leads', json={
            'isim': 'Test Kullanıcı', 'telefon': '05551234567', 'mesaj': 'Temizlik'
        })
        self.assertEqual(created.status_code, 201)
        self.assertEqual(self.client.get('/api/leads').status_code, 401)
        listed = self.client.get('/api/leads', headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.get_json()['leadler']), 1)

    def test_guide_aliases(self):
        created = self.client.post('/api/adaylar', json={
            'isim': 'Alias Test', 'telefon': '+905551234567', 'mesaj': ''
        })
        self.assertEqual(created.status_code, 201)
        listed = self.client.get('/api/adaylar', headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(listed.status_code, 200)

    def test_invalid_phone(self):
        with self.assertRaises(ValidationError):
            validate_lead({'isim': 'Test', 'telefon': 'abc', 'mesaj': ''})

    def test_limiter(self):
        limiter = RequestLimiter()
        self.assertTrue(limiter.allowed('x', 1))
        self.assertFalse(limiter.allowed('x', 1))


if __name__ == '__main__':
    unittest.main()
