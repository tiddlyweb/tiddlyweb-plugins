"""
JSONP serialization for TiddlyWeb.

If jsonp_callback is in tiddlyweb.query, send the results as
jsonp, otherwise, do the normal JSON results.
"""


from tiddlyweb.serializations.json import Serialization as JSON

SERIALIZERS = {
        'application/json': ['tiddlywebplugins.jsonp', 'application/json; charset=UTF-8'],
        }


def init(config):
    config['serializers'].update(SERIALIZERS)


class Serialization(JSON):

    def _get_jsonp(self):
        jsonp = self.environ['tiddlyweb.query'].get('jsonp_callback', [None])[0]
        if jsonp:
            return '%s(' % jsonp, ')'
        else:
            return '', ''

    def list_recipes(self, recipes):
        prefix, suffix = self._get_jsonp()
        return prefix + JSON.list_recipes(self, recipes) + suffix

    def list_bags(self, bags):
        prefix, suffix = self._get_jsonp()
        return prefix + JSON.list_bags(self, bags) + suffix

    def list_tiddlers(self, bag):
        prefix, suffix = self._get_jsonp()
        return prefix + JSON.list_tiddlers(self, bag) + suffix

    def recipe_as(self, recipe):
        prefix, suffix = self._get_jsonp()
        return prefix + JSON.recipe_as(self, recipe) + suffix

    def bag_as(self, bag):
        prefix, suffix = self._get_jsonp()
        return prefix + JSON.bag_as(self, bag) + suffix

    def tiddler_as(self, tiddler):
        prefix, suffix = self._get_jsonp()
        return prefix + JSON.tiddler_as(self, tiddler) + suffix
