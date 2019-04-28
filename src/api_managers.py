import requests

TOBOT_ID = 'aoql74lx3merlu6t3od1wcfhn44u72'
TOBURR_USER_ID = '77780959'
AUTH_PATH = 'apiauth.txt'

class TwitchAPIManager:
    """
    Handles direct interactions with Twitch APIs
    """

    def __init__(self, auth=None,id=TOBOT_ID):
        """
        Initialize necessary info for API calls
        """
        self.clientid = id
        if auth == None:
            try:
                f = open(AUTH_PATH)
                auth = f.read()
                f.close()
            except:
                print 'ERROR: could not find apiauth.txt'
                auth = ''
        self.authcode = auth
        self.token = ''
        f = open('user_access.txt')
        self.user_token = f.read()
        f.close()
        f = open('user_refresh.txt')
        self.user_refresh_token = f.read()
        f.close()

    def _print_error_message(self, response):
        print 'Status:',response.status_code
        try:
            print response.json()
        except ValueError: # Catch responses in non-json format
            print 'URL:',response.url
            print 'Text:',response.text
        print ''

    def _acquire_access_token(self, scope=''):
        """
        Fetches a new access token from the Twitch API.
        If request is successful, sets Manager token to new token.
        If failure, sets Manager token to empty string
        """
        success = False
        resp = requests.post('https://id.twitch.tv/oauth2/token?client_id='+self.clientid+'&client_secret='+self.authcode+'&grant_type=client_credentials&scope='+scope)
        if resp.status_code == requests.codes.ok:
            success = True
            self.token = resp.json()['access_token']
        else:
            print 'ERROR failed to acquire access token'
            self._print_error_message(resp)
        return success

    def _revoke_access_token(self):
        """
        Tells Twitch to dispose of the current access token. Handy for the
        sake of forcing the bot to get a new one.
        """
        resp = requests.post('https://id.twitch.tv/oauth2/revoke?client_id='+self.clientid+'&token='+self.token)
        success = resp.status_code == requests.codes.ok
        # If revocation went fine, reset our internal token
        if success:
            self.token = ''
        else:
            print 'ERROR on revoking access token'
            self._print_error_message(resp)
        return success

    def _refresh_user_token(self):
        resp = requests.post('https://id.twitch.tv/oauth2/token--data-urlencode?grant_type=refresh_token&refresh_token='+self.user_refresh_token+'&client_id='+self.clientid+'&client_secret='+self.clientauth)
        success = resp.status_code == requests.codes.ok
        if success:
            jresp = resp.json()
            f = open('user_access.txt', 'w')
            f.write(jresp['access_token'])
            self.user_token = jresp['access_token']
            f.close()
            f = open('user_refresh.txt', 'w')
            f.write(jresp['refresh_token'])
            self.user_refresh_token = jresp['refresh_token']
            f.close()
        else:
            print 'ERROR on user token refresh:'
            self._print_error_message(resp)
        return success

    def request_send_loop(self, request_func, params):
        """
        Repeats a request until it definitively succeeds or fails
        """
        need_refresh = True
        while need_refresh:
            need_refresh = False
            resp = request_func(*params)
            success = resp.status_code == requests.codes.ok
            if success:
                pass
            elif resp.status_code == 401: #401 = Unauthorized, which COULD mean our token's just expired
                for guy in resp.headers.items():
                    print guy
                print ''
                if 'WWW-Authenticate' in resp.headers:
                    need_refresh = True
                    self._refresh_user_token()
            else:
                print 'ERROR while setting stream title'
                self._print_error_message(resp)
        return success

    def do_set_stream_title_request(self, title):
        headers = {
            'Client-ID': self.clientid,
            'Accept': 'application/vnd.twitchtv.v5+json',
            'Authorization': 'OAuth ' + self.user_token,
            'Content-Type': 'application/json',
        }

        data = '{"channel": {"status": "'+title+'"}}'
        return requests.put('https://api.twitch.tv/kraken/channels/'+TOBURR_USER_ID, headers=headers, data=data)

    def set_stream_title(self, title):
        return self.request_send_loop(self.do_set_stream_title_request, [title])

    def do_set_stream_game_request(self, game):
        headers = {
            'Client-ID': self.clientid,
            'Accept': 'application/vnd.twitchtv.v5+json',
            'Authorization': 'OAuth ' + self.user_token,
            'Content-Type': 'application/json',
        }
        data = '{"channel": {"game": "'+game+'"}}'
        return requests.put('https://api.twitch.tv/kraken/channels/'+TOBURR_USER_ID, headers=headers, data=data)

    def set_stream_game(self, game):
        return self.request_send_loop(self.do_set_stream_game_request, [game])

    def set_clientid(self, newid):
        """
        Sets the new clientid. Used in the event that the default id doesn't
        work for whatever reason.
        """
        self.clientid = newid
