"""
All the behaviors toburobo is capable of

All return values must be strings which the bot replies to the IRC server with. Return None for
the bot to not reply at all
"""

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

# A default map of supported commands, and the corresponding number of arguments for
# each command.
DEFAULT_COMMANDS = {'!hi': sayhi, '!hello': sayhello, 'gl': saythanks}
DEFAULT_ARGC = {'!hi': 0, '!hello': 1, 'gl': 0}
