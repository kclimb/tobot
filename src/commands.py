"""
All the behaviors toburobo is capable of

All return values must be strings which the bot replies to the IRC server with. Return None for
the bot to not reply at all
"""

def sayhi():
	return 'hi :)'

def sayhello(name):
	return 'hello '+name+'!'

def nop():
	return None
