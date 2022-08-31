import requests
import urllib

TOBOT_ID = 'aoql74lx3merlu6t3od1wcfhn44u72'
TOBURR_USER_ID = '77780959'
TWITCH_AUTH_PATH = 'twitchapiauth.txt'
SRC_AUTH_PATH = ''

class TwitchAPIManager:
    """
    Handles direct interactions with Twitch APIs
    """

    def __init__(self, auth=None,id=TOBOT_ID, v=True):
        """
        Initialize necessary info for API calls
        """
        self.clientid = id
        self.verbose = v
        if auth == None:
            try:
                f = open(TWITCH_AUTH_PATH)
                auth = f.read()
                f.close()
            except:
                if v:
                    print('ERROR: could not find twitchapiauth.txt')
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
        print('Status:',response.status_code)
        try:
            print(response.json())
        except ValueError: # Catch responses in non-json format
            print('URL:',response.url)
            print('Text:',response.text)
        print('')

    ############################# ACCESS TOKEN THINGS #############################

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
        elif self.verbose:
            print('ERROR failed to acquire access token')
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
        elif self.verbose:
            print('ERROR on revoking access token')
            self._print_error_message(resp)
        return success

    def _refresh_user_token(self):
        """
        Sends a user token refresh request to Twitch. Updates the user token
        and refresh token on success.
        """
        if self.verbose:
            print('REFRESHING...')
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = 'grant_type=refresh_token&refresh_token='+self.user_refresh_token+'&client_id='+self.clientid+'&client_secret='+self.authcode

        resp = requests.post('https://id.twitch.tv/oauth2/token', headers=headers, data=data)
        if self.verbose:
            print(resp.status_code)
            print(resp.json())
        if resp.status_code == requests.codes.ok or resp.status_code == requests.codes.no_content:
            jresp = resp.json()
            f = open('user_access.txt', 'w')
            f.write(jresp['access_token'])
            self.user_token = jresp['access_token']
            f.close()
            f = open('user_refresh.txt', 'w')
            f.write(jresp['refresh_token'])
            self.user_refresh_token = jresp['refresh_token']
            f.close()
        elif self.verbose:
            print('ERROR on user token refresh:')
            self._print_error_message(resp)
        return success

    ########################### HTTP REQUEST LOGIC ################################

    def _request_send_loop(self, request_func, params):
        """
        Repeats a request function until it definitively succeeds or fails.

        In practice, this loop should succeed on the first pass, unless the
        current user OAuth token is expired, in which case a refresh is performed,
        and the request should succeed on the second pass.

        All commands which send requests that supply a user OAuth token should
        plug the request into this function to guarantee it doesn't fail due to
        an expired token.
        """
        resp = self._request_send_loop_get_response(request_func, params)
        success = resp.status_code == requests.codes.ok or resp.status_code == requests.codes.no_content
        return success

    def _request_send_loop_get_response(self, request_func, params):
        """
        Repeats a request function until it definitively succeeds or fails.

        In practice, this loop should succeed on the first pass, unless the
        current user OAuth token is expired, in which case a refresh is performed,
        and the request should succeed on the second pass.

        All commands which send requests that supply a user OAuth token should
        plug the request into this function to guarantee it doesn't fail due to
        an expired token.
        """
        need_refresh = True
        while need_refresh:
            need_refresh = False
            resp = request_func(*params)
            success = resp.status_code == requests.codes.ok or resp.status_code == requests.codes.no_content
            if success:
                pass
            elif resp.status_code == 401: #401 = Unauthorized, which COULD mean our token's just expired
                #for guy in resp.headers.items():
                #    print guy
                #print ''
                if self.verbose:
                    print(resp.json())
                    print('')
                #if 'WWW-Authenticate' in resp.headers: # Twitch claims this check is necessary but seems currently unimplemented on their side?
                need_refresh = True
                self._refresh_user_token()
            elif self.verbose:
                print('ERROR while setting stream title')
                self._print_error_message(resp)
        return resp

    def _update_channel_request(self, channelid, headers, data):
        """
        Sends a PATCH request for user channel data.
        """
        return requests.patch('https://api.twitch.tv/helix/channels?broadcaster_id='+channelid, headers=headers, data=data)

    def _get_channel_request(self):
        """
        Sends a GET request for user channel data.
        """
        headers = {
            'Client-ID': self.clientid,
            'Authorization': 'Bearer ' + self.user_token,
        }
        return requests.get('https://api.twitch.tv/helix/channels?broadcaster_id='+TOBURR_USER_ID, headers=headers)

    def _get_gameid_request(self, gamename, headers):
        """
        Sends a GET request to get a game's internal ID from its name.
        header
        """
        return requests.get("https://api.twitch.tv/helix/games?name="+gamename,headers=headers)

    ############################ COMMAND LOGIC #####################################

    def _do_set_stream_title_request(self, title):
        """
        Sends request for !settitle
        """
        headers = {
            'Client-ID': self.clientid,
            'Accept': 'application/vnd.twitchtv.v5+json',
            'Authorization': 'Bearer ' + self.user_token,
            'Content-Type': 'application/json',
        }

        data = '{"title": "'+title+'"}'
        return self._update_channel_request(TOBURR_USER_ID, headers, data)

    def set_stream_title(self, title):
        """
        Entry point for !settitle
        """
        return self._request_send_loop(self._do_set_stream_title_request, [title])

    def _do_set_stream_game_request(self, gameid):
        """
        Sends request for !setgame
        """
        headers = {
            'Client-ID': self.clientid,
            'Accept': 'application/vnd.twitchtv.v5+json',
            'Authorization': 'Bearer ' + self.user_token,
            'Content-Type': 'application/json',
        }
        data = '{"game_id": "'+gameid+'"}'
        return self._update_channel_request(TOBURR_USER_ID, headers, data)

    def set_stream_game(self, game):
        """
        Entry point for !setgame
        """
        headers = {
            'Client-ID': self.clientid,
            'Authorization': 'Bearer ' + self.user_token,
        }
        gameid_response = self._request_send_loop_get_response(self._get_gameid_request, [game, headers])

        if gameid_response.status_code < 300 and gameid_response.status_code >= 200: # we got some type of success
            gameid = gameid_response.json()['data'][0]['id']
        else:
            print("ERROR in fetching gameid")
            return False
        
        return self._request_send_loop(self._do_set_stream_game_request, [gameid])

    def get_stream_title(self):
        """
        Entry point for !title
        """
        resp = self._request_send_loop_get_response(self._get_channel_request, [])
        return resp.json()['data'][0]['title']

    def get_stream_game(self):
        """
        Entry point for !game
        """
        resp = self._request_send_loop_get_response(self._get_channel_request, [])
        print(resp.json())
        return resp.json()['data'][0]['game_name']

    #################################### MISC ######################################

    def set_clientid(self, newid):
        """
        Sets the new clientid. Used in the event that the default id doesn't
        work for whatever reason.
        """
        self.clientid = newid

#####################################################################################
#################################### SRC Stuff ######################################
#####################################################################################

class SpeedrunComAPIManager:
    """
    Handles interactions with speedrun.com
    """

    def __init__(self):
        self.gamecache = {}

    def _get_game_name_request(self,name):
        """
        Returns a speedrun.com API request querying the games list by name.

        This should generally only be used to fetch game id. All other API
        game queries should use _get_game_id_request once they have the id.
        """
        url_name = urllib.quote(name)
        return requests.get("https://speedrun.com/api/v1/games?name="+url_name)

    def _get_game_id_request(self,id,suffix=""):
        """
        Returns a request for info on a certain game on speedrun.com.

        "id" is the game's ID on SRC, and "suffix" is the rest of the request
        after the ID if the request wants specific info (it usually does)
        """
        if suffix == None:
            suffix = ""
        return requests.get("https://speedrun.com/api/v1/games/"+id+suffix)

    def _get_user_id_request(self,id,suffix=""):
        if suffix == None:
            suffix = ""
        return requests.get("https://speedrun.com/api/v1/users/"+id+suffix)

    def _get_game_id(self,name):
        if name in self.gamecache:
            return self.gamecache[name]
        requestdata = self._get_game_name_request(name).json()['data']
        if len(requestdata) == 0:
            return None
        id = requestdata[0]['id']
        self.gamecache[name] = id
        return id

    def get_top_times(self,gamename,cat_num=0):
        id = self._get_game_id(gamename)
        if id == None:
            return None
        rundata = self._get_game_id_request(id,"/records").json()['data']
        if len(rundata) <= cat_num:
            cat_num = 0 # If provided category number doesn't exist, default to the first one
        return rundata[cat_num]['runs']

    def get_username(self,userid):
        return self._get_user_id_request(userid).json()['data']['names']['international']
