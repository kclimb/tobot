"""
All the behaviors toburobo is capable of

All return values must be strings which the bot replies to the IRC server with. Return None for
the bot to not reply at all
"""
import json
import random

GAME_ABBREVIATIONS = json.loads(open('gamecodes.txt').read())
TEXT_COMMANDS = {#json.loads(open('textcommands.txt').read())
	'!hi': 'hi :)',
	'gl': 'thanks',
	'!wr': "it doesn't matter :)",
}

def isTextCommand(key):
	return key in TEXT_COMMANDS

def doTextCommand(key):
	try:
		return TEXT_COMMANDS[key]
	except KeyError:
		return None

def sayhello(name):
	"""
	Yes, this bot does have multiple greeting commands. Saying hi is important.
	"""
	return 'hello '+name+'! Welcome to the stream toburrArr'

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

	try:
		game = GAME_ABBREVIATIONS[game]
	except KeyError:
		pass
	success = api_mgr.set_stream_game(game)
	if success:
		return 'Game is set to ' + game
	return 'Failed to set game'

def dr():
	"""
	Returns the name of the video game franchise, Danganronpa. Kind of.
	"""
	return random.choice(DANGAN) + ' ' + random.choice(RONPA)

def addgamename(code, fullname):
	if code not in GAME_ABBREVIATIONS:
		#GAME_ABBREVIATIONS[code] = fullname
		f = open('gamecodes.txt','w')
		f.write(json.dumps(GAME_ABBREVIATIONS))
		f.close()
		return 'Successfully added abbreviation '+code+' for game: '+fullname+'.'
	return 'The abbreviation '+code+' is already in use for the game: '+GAME_ABBREVIATIONS[code] +'.'

def editgamename(code, newname):
	if code in GAME_ABBREVIATIONS:
		GAME_ABBREVIATIONS[code] = newname
		f = open('gamecodes.txt','w')
		f.write(json.dumps(GAME_ABBREVIATIONS))
		f.close()
		return 'Successfully added abbreviation '+code+' for game: '+fullname+'.'
	return addgamename(code, newname)

def removegamename(code):
	val = GAME_ABBREVIATIONS.pop(code, None)
	if val == None:
		return 'Abbreviation '+code+' not found.'
	f = open('gamecodes.txt','w')
	f.write(json.dumps(GAME_ABBREVIATIONS))
	f.close()
	return 'Successfully removed abbreviation '+code+'.'

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
	'!addgamename':addgamename,'!commands':list_commands,'!dr':dr,'!editgamename':editgamename,'!game':saygame,'!hello':sayhello,'!removegamename':removegamename,'!setgame':setgame,'!settitle':settitle,
	'!title':saytitle,
}
DEFAULT_ARGC = {'!addgamename':2,'!commands':0,'!dr':0,'!editgamename':2,'!game':0,'!hello':1,'!removegamename':1,'!setgame':1,'!settitle':1,'!title':0,}
NEEDS_METADATA = set([setgame, settitle])
NEEDS_API = set([saygame, saytitle, setgame, settitle])

# Other handy data things
DANGAN = ['danger', 'doggone', 'draugr', 'dagnabbit', 'dungeon', 'drumbo', 'dagger', 'dansgame', 'daenerys', 'dungarees', 'dunsparce', 'diego', 'dang']
RONPA = ['ron paul', 'romper', 'rumbo', 'rumble', 'rumpus', 'rambo', 'renpy', 'rumba', 'ringo', 'rondo', 'papa']
