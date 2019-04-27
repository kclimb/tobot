import requests

TOBOT_ID = 'aoql74lx3merlu6t3od1wcfhn44u72'
AUTH_PATH = 'apiauth.txt'

class APIManager:
    def __init__(self, auth=None,id=TOBOT_ID):
        self.clientid = id
        if auth == None:
            try:
                f.open(AUTH_PATH)
                auth = f.read()
            except:
                print 'ERROR: could not find apiauth.txt'
                auth = ''
        self.authcode = auth
        self.token = ''

    def acquire_access_token():
        success = False
        resp = requests.post('https://id.twitch.tv/oauth2/token?client_id='+self.clientid+'&client_secret='+self.authcode+'&grant_type=client_credentials')
        if resp.status_code == requests.codes.ok:
            success = True
            token = resp.json()['access_token']
        return success, token

    def revoke_access_token():
        resp = requests.post('https://id.twitch.tv/oauth2/revoke?client_id='+self.clientid+'&token='+self.token)
        return resp.status_code == requests.codes.ok
