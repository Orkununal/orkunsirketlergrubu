"""Harici yapay zekâ sağlayıcısı ile iletişim katmanı."""
import requests
from ayarlar import Config


class AIServiceError(Exception):
    """Sağlayıcının teknik hata ayrıntılarını kullanıcıdan saklar."""


class AIService:
    def __init__(self, settings=None):
        self.settings = settings if settings is not None else {
            key: getattr(Config, key) for key in dir(Config) if key.isupper()
        }

    @property
    def demo_mode(self):
        return self.settings['AI_PROVIDER'] == 'demo' or not self.settings['GROQ_API_KEY']

    def _sistem_talimati(self):
        return self.settings['BUSINESS_CONTEXT']

    def yanit_uret(self, mesaj, gecmis=None):
        if self.demo_mode:
            return ('Demo modu: Bu yanıt yapay zekâ tarafından üretilmedi. '
                    'Hizmet ihtiyacınızı aşağıdaki teklif formuna yazıp adınızı ve '
                    'telefonunuzu bırakarak bir görüşme talebi oluşturabilirsiniz.')
        if self.settings['AI_PROVIDER'] != 'groq':
            raise AIServiceError('Yapay zekâ sağlayıcısı yapılandırılamadı.')
        messages = [{'role': 'system', 'content': self._sistem_talimati()}]
        messages.extend(gecmis or [])
        messages.append({'role': 'user', 'content': mesaj})
        return self._groq_istegi(messages)

    def _groq_istegi(self, messages):
        try:
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={'Authorization': f"Bearer {self.settings['GROQ_API_KEY']}"},
                json={'model': self.settings['AI_MODEL'], 'messages': messages,
                      'temperature': 0.4, 'max_completion_tokens': 500},
                timeout=self.settings['AI_TIMEOUT'],
            )
            response.raise_for_status()
            answer = response.json()['choices'][0]['message']['content']
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError('Boş yanıt')
            return answer.strip()
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as exc:
            raise AIServiceError('Asistan şu anda yanıt veremiyor. Lütfen biraz sonra tekrar deneyin.') from exc


ai_service = AIService()
