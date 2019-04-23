"""
All the behaviors toburobo is capable of

All return values must be strings which the bot replies to the IRC server with. Return None for
the bot to not reply at all
"""
import random

def sayhi():
	return 'hi :)'

def sayhello(name):
	return 'hello '+name+'!'

def saythanks():
	return 'thanks'

def settitle(title):
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


# A default map of supported commands, and the corresponding number of arguments for
# each command.
DEFAULT_COMMANDS = {'!commands':list_commands,'!dr':dr,'!hi':sayhi,'!hello':sayhello,'!wr':wr,'gl':saythanks}
DEFAULT_ARGC = {'!commands':0,'!dr':0,'!hi': 0,'!hello':1,'!wr':0,'gl':0}

# Other handy data things
DANGAN = ['danger', 'doggone', 'draugr', 'dagnabbit', 'dungeon', 'drumbo', 'dagger', 'dansgame', 'daenerys', 'dungarees', 'dunsparce']
RONPA = ['ron paul', 'romper', 'rumbo', 'rumble', 'rumpus', 'rambo', 'renpy', 'rumba', 'ringo', 'rondo']
