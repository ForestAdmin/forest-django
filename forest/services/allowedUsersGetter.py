import requests
from django.conf import settings

def get_allowed_users(rendering_id):
    url = 'https://forestadmin-server.herokuapp.com'
    #TODO: Tell forest rendering ID isn't used in request
    url += '/forest/renderings/%s/allowed-users' % rendering_id
    #TODO: key in config
    secret_key = 'a822da157aec0b2831a95e097e0b9a7a67b282cbbc1ec4b65185deaa019c102e'
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
