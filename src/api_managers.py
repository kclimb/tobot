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
                f.open(AUTH_PATH)
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

    def _print_error_message(response):
        print 'Status:',response.status_code
        try:
            print response.json()
        except ValueError: # Catch responses in non-json format
            print 'URL:',response.url
            print 'Text:',response.text
        print ''

    def _acquire_access_token(scope=''):
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

    def _revoke_access_token():
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

    def _refresh_user_token():
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

    def set_stream_title(title):
        need_refresh = True
        # Loop until we either succeed for fail for non-expired-token reasons
        while need_refresh:
            need_refresh = False
            headers = {
        		'Client-ID': self.clientid,
        		'Accept': 'application/vnd.twitchtv.v5+json',
        		'Authorization': 'OAuth ' + self.user_token,
                'Content-Type': 'application/json',
        	}

            data = '{"channel": {"status": "'+title+'"}}'
            resp = requests.put('https://api.twitch.tv/kraken/channels/'+TOBURR_USER_ID, headers=headers, data=data)
            success = resp.status_code == requests.codes.ok
            if success:
                pass
            elif resp.status_code == 401 and 'WWW-Authenticate' in r.headers: # Change None to the actual response to check
                need_refresh = True
                self._refresh_user_token()
            else:
                print 'ERROR while setting stream title'
                self._print_error_message(resp)
        return success

    def set_clientid(newid):
        """
        Sets the new clientid. Used in the event that the default id doesn't
        work for whatever reason.
        """
        self.clientid = newid
