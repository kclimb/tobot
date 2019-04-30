"""
All the behaviors toburobo is capable of

All return values must be strings which the bot replies to the IRC server with. Return None for
the bot to not reply at all
"""
import random

def sayhi():
	"""
	:)
	"""
	return 'hi :)'

def sayhello(name):
	"""
	Yes, this bot does have multiple greeting commands. Saying hi is important.
	"""
	return 'hello '+name+'!'

def saythanks():
	"""
	This bot is polite, dammit.
	"""
	return 'thanks'

def saytitle(api_mgr):
	"""
	Returns the title of the stream. Needs Twitch API access.
	"""
	return 'Stream title is: '+api_mgr.get_stream_title()

def settitle(title, metadata, api_mgr):
	"""
	Allows mods and broadcasters to set the title of the stream game.
	Note that the 'title' parameter is specified by the chat message, but
	user_type is supplied by this bot from parsing the chat message's metadata.
	"""
	hdrs = metadata['headers']
	channel = metadata['channel']
	print 'HDRS'
	for guy in hdrs.items():
		print guy
	# If this person isn't a mod or the broadcaster, do a !title instead
	if hdrs['mod'] == '0' and channel != hdrs['display-name'].lower():
		return saytitle(api_mgr)

	success = api_mgr.set_stream_title(title)
	if success:
		return 'Title is set to ' + title
	return 'Failed to set title'

def saygame(api_mgr):
	"""
	Returns the title of the current game. Needs Twitch API access.
	"""
	return 'Game is: '+api_mgr.get_stream_game()

def setgame(game, metadata, api_mgr):
	hdrs = metadata['headers']
	channel = metadata['channel']
	# If this person isn't a mod or the broadcaster, do a !title instead
	if hdrs['mod'] == '0' and channel != hdrs['display-name'].lower():
		return saygame(api_mgr)

	success = api_mgr.set_stream_game(game)
	if success:
		return 'Game is set to ' + game
	return 'Failed to set game'

def nop():
	"""
	It does nothing. Leftover from when I thought it was a good idea to force
	the bot to have a designated response for every type of chat message.
	"""
	return None

def dr():
	"""
	Returns the name of the video game franchise, Danganronpa. Kind of.
	"""
	return random.choice(DANGAN) + ' ' + random.choice(RONPA)

def wr():
	"""
	Fetches the World Record for the main speedrunning category of the current game.

	Yes, I am very aware it just returns a string.
	"""
	return "it doesn't matter :)"

def list_commands():
	"""
	Returns a list of all* commands currently supported by this bot.

	*Well some things are more fun kept a secret**

	**Ok sure it's not a secret if you just look at the commands map. But where's
	the fun in that? Killjoy.
	"""
	retstring = ''
	for guy in DEFAULT_COMMANDS.keys():
		if guy.startswith('!'):
			retstring = retstring + guy + '\r'
	return retstring

def missing_token_error(expected, actual):
	parameters = 'parameters'
	if expected == '1':
		parameters = 'parameter'
	return "Command failed. Expected "+expected+" "+parameters+" but received "+actual+"."

def missing_end_quote_error():
	return "Command failed. Could not find ending quotation mark. Make sure the end quote is at the end of a word."

# A default map of supported commands, and the corresponding number of user-supplied arguments for each command.
# Note there may be more actual arguments that toburobo needs to supply (from message headers, credentials, etc)
DEFAULT_COMMANDS = {
	'!commands':list_commands,'!dr':dr,'!game':saygame,'!hi':sayhi,'!hello':sayhello,'!setgame':setgame,'!settitle':settitle,
	'!title':saytitle,'!wr':wr,'gl':saythanks
}
DEFAULT_ARGC = {'!commands':0,'!dr':0,'!game':0,'!hi': 0,'!hello':1,'!setgame':1,'!settitle':1,'!title':0,'!wr':0,'gl':0}
NEEDS_METADATA = set([setgame, settitle])
NEEDS_API = set([saygame, saytitle, setgame, settitle])

# Other handy data things
DANGAN = ['danger', 'doggone', 'draugr', 'dagnabbit', 'dungeon', 'drumbo', 'dagger', 'dansgame', 'daenerys', 'dungarees', 'dunsparce', 'diego', 'dang']
RONPA = ['ron paul', 'romper', 'rumbo', 'rumble', 'rumpus', 'rambo', 'renpy', 'rumba', 'ringo', 'rondo', 'papa']
