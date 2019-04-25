"""
All the behaviors toburobo is capable of

All return values must be strings which the bot replies to the IRC server with. Return None for
the bot to not reply at all
"""
import random
#import requests

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

def settitle(title, user_type):
	"""
	Allows mods and broadcasters to set the title of the stream game.
	Note that the 'title' parameter is specified by the chat message, but
	user_type is supplied by this bot from parsing the chat message's metadata.
	"""
	f = open('mydata.txt')
	headers = {
		'Client-ID': '***REAL CLIENT ID HERE',
		'Accept': 'PRETTY SURE V5 IS DEPRECATED SO CHANGE ME',
		'Authorization': 'OAuth ' + f.read()
	}

	data = {
		'channel[status]': title
	}
	#response = requests.put('https://api.twitch.tv/kraken/channels/***CHANGE ME TO THE REAL CHANNEL ID***', headers=headers, data=data)
	return 'Title is set to ' + title

def title():
	"""
	Returns the title of the current game. Needs Twitch API access.
	"""
	return "Not implemented yet :("

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


# A default map of supported commands, and the corresponding number of user-supplied arguments for each command.
# Note there may be more actual arguments that toburobo needs to supply (from message headers, credentials, etc)
DEFAULT_COMMANDS = {'!commands':list_commands,'!dr':dr,'!hi':sayhi,'!hello':sayhello,'!title':title,'!wr':wr,'gl':saythanks}
DEFAULT_ARGC = {'!commands':0,'!dr':0,'!hi': 0,'!hello':1,'settitle':1,'!title':0,'!wr':0,'gl':0}
MIN_ARGC = {} #{'!title':0} This was a terrible idea should probably delete this but you never know, huh

# Other handy data things
DANGAN = ['danger', 'doggone', 'draugr', 'dagnabbit', 'dungeon', 'drumbo', 'dagger', 'dansgame', 'daenerys', 'dungarees', 'dunsparce']
RONPA = ['ron paul', 'romper', 'rumbo', 'rumble', 'rumpus', 'rambo', 'renpy', 'rumba', 'ringo', 'rondo']
