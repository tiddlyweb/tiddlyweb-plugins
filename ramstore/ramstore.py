"""
A ramstore.

As in, a store which stores stuff in RAM.

Obviously not a great solution if you want persistence,
but good if you want to do some debugging, profiling, or
have some need for a bag or do that is fast and you have
ways to control its persistence and shareability.
"""

TIDDLERS = {}
BAGS = {}
RECIPES = {}
