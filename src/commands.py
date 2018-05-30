"""
All the behaviors toburobo is capable of

All return values must be strings which the bot replies to the IRC server with. Return None for
the bot to not reply at all
"""

def sayhi(name = ''):
	return 'hi ' + name + ' :)'

def nop():
	return None