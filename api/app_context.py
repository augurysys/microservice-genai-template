# core/context.py
from typing import Optional


class AppContext:
    def __init__(self):
        self.clients = dict()
        self.oauth_client = None

    def set(self, key, client):
        self.clients[key] = client
        return self

    def get(self, key) -> Optional[any]:
        return self.clients.get(key, None)
