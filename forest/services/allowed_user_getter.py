import os
import requests
from django.conf import settings

def get_allowed_users(rendering_id):
    url = os.getenv('FOREST_URL', settings.FOREST_URL)
    #TODO: Tell forest rendering ID isn't used in request
    url += '/forest/renderings/%s/allowed-users' % rendering_id
    #TODO: key in config
    secret_key = os.getenv('FOREST_SECRET_KEY', settings.FOREST_SECRET_KEY)
    headers = {
        'forest-secret-key':  secret_key,
        'Content-Type': 'application/json'
    }
    r = requests.get(url, headers=headers)
    allowedUsers = []
    for data in r.json()['data']:
        user = data['attributes']
        user['id'] = data['id']
        allowedUsers.append(user)
    return allowedUsers
