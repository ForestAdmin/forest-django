import json
import requests

from django.apps import AppConfig
from forest.generators.schemas import api_map


class ForestConfig(AppConfig):
    name = 'forest'
    verbose_name = "My Forest Connector"
    def ready(self):
        apimap = api_map.generate()
        url = 'https://forestadmin-server.herokuapp.com'
        url += '/forest/apimaps'
        secret_key = '5135a1c7e29787b300f1f6326dfe8819b147aad72807e0f28ae9a82209e45076'
        headers = {
            'forest-secret-key':  secret_key,
            'Content-Type': 'application/json'
        }
        req = requests.post(url, data=json.dumps(apimap), headers=headers)
