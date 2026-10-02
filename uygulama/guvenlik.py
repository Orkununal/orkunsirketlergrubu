"""Yönetici doğrulaması ve bellek içi istek sınırlayıcı."""
import hmac
import time
from collections import OrderedDict
from threading import Lock
from flask import current_app, request


def admin_authorized():
    token = current_app.config['ADMIN_API_TOKEN']
    supplied = request.headers.get('Authorization', '')
    expected = f'Bearer {token}'
    return bool(token) and hmac.compare_digest(supplied.encode(), expected.encode())


class RequestLimiter:
    def __init__(self):
        self.buckets = OrderedDict()
        self.lock = Lock()

    def allowed(self, key, limit):
        now = time.monotonic()
        with self.lock:
            start, count = self.buckets.get(key, (now, 0))
            if now - start >= 60:
                start, count = now, 0
            self.buckets[key] = (start, count + 1)
            self.buckets.move_to_end(key)
            if len(self.buckets) > 10000:
                self.buckets.popitem(last=False)
            return count < limit
