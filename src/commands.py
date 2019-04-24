"""
All the behaviors toburobo is capable of

All return values must be strings which the bot replies to the IRC server with. Return None for
the bot to not reply at all
"""
import random
#import requests

def sayhi():
	return 'hi :)'

def sayhello(name):
	return 'hello '+name+'!'

def saythanks():
	return 'thanks'

def title(title, user_type):
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

def nop():
	return None

def dr():
	return random.choice(DANGAN) + ' ' + random.choice(RONPA)

def wr():
	return "it doesn't matter :)"

def list_commands():
	retstring = ''
	for guy in DEFAULT_COMMANDS.keys():
		if guy.startswith('!'):
			retstring = retstring + guy + '\r'
	return retstring


# A default map of supported commands, and the corresponding number of user-supplied arguments for each command.
# Note there may be more actual arguments that toburobo needs to supply (from message headers, credentials, etc)
DEFAULT_COMMANDS = {'!commands':list_commands,'!dr':dr,'!hi':sayhi,'!hello':sayhello,'!title':title,'!wr':wr,'gl':saythanks}
DEFAULT_ARGC = {'!commands':0,'!dr':0,'!hi': 0,'!hello':1,'!title':1,'!wr':0,'gl':0}
MIN_ARGC = {} #{'!title':0}

# Other handy data things
DANGAN = ['danger', 'doggone', 'draugr', 'dagnabbit', 'dungeon', 'drumbo', 'dagger', 'dansgame', 'daenerys', 'dungarees', 'dunsparce']
RONPA = ['ron paul', 'romper', 'rumbo', 'rumble', 'rumpus', 'rambo', 'renpy', 'rumba', 'ringo', 'rondo']
