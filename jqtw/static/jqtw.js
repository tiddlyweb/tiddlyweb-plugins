
TiddlyWeb = {
    routes: {
        root: '{prefix}/',
        recipes: '{prefix}/recipes',
        bags: '{prefix}/bags',
        bag: '{prefix}/bags/{name}',
        recipe: '{prefix}/recipes/{name}',
        bag_tiddlers: '{prefix}/bags/{container_name}/tiddlers',
        recipe_tiddlers: '{prefix}/recipes/{container_name}/tiddlers',
        tiddler: '{prefix}/{container_type}/{container_name}/tiddlers/{title}',
        bag_tiddler_revisions: '{prefix}/bags/{container_name}/tiddlers/{title}/revisions',
        recipe_tiddler_revisions: '{prefix}/recipes/{container_name}/tiddlers/{title}/revisions',
        bag_tiddler_revision: '{prefix}/bags/{container_name}/tiddlers/{title}/revisions/{id}',
        recipe_tiddler_revision: '{prefix}/recipes/{container_name}/tiddlers/{title}/revisions/{id}',
        search: '{prefix}/search'
    }
};

TiddlyWeb.extend = function(subClass, baseClass) {
    function inheritance() {}
    inheritance.prototype = baseClass.prototype;
    subClass.prototype = new inheritance();
    subClass.prototype.constructor = subClass;
    subClass.baseConstructor = baseClass;
    subClass.superClass = baseClass.prototype;
}

//Resource
TiddlyWeb.Resource = function() {
    this.prefix = '';
    this.container_id = '#container';
}

TiddlyWeb.Resource.prototype.route = function() {
    return this.format(TiddlyWeb.routes[this.type]);
}

TiddlyWeb.Resource.prototype.format = function(content) {
    var self = this;
    content = content.replace(/{\w+}/g, function(a) {
        var a = a.replace(/{|}/g, '');
        return self[a];
    });
    return content;
}

TiddlyWeb.Resource.prototype.get = function(present) {
    var self = this;
    $.ajax({
        type: "GET",
        dataType: 'json',
        url: self.route(),
        success: function(data) {self.process(data);if(present) self.presenter()},
        });
}

TiddlyWeb.Resource.prototype.process = function(data) {
    this.data = data;
}

TiddlyWeb.Resource.prototype.presenter = function() {
    $(this.container_id).append('<p>' + this.type + ': ' + this.data + '</p>');
}

//Recipes
TiddlyWeb.Recipes = function() {
    TiddlyWeb.Recipes.baseConstructor.call(this);
    this.type = 'recipes';
}

TiddlyWeb.extend(TiddlyWeb.Recipes, TiddlyWeb.Resource);

//Bags
TiddlyWeb.Bags = function() {
    TiddlyWeb.Bags.baseConstructor.call(this);
    this.type = 'bags';
}

TiddlyWeb.extend(TiddlyWeb.Bags, TiddlyWeb.Resource);

//Bag
TiddlyWeb.Bag = function(name) {
    TiddlyWeb.Bag.baseConstructor.call(this);
    this.type = 'bag';
    this.name = name;
}

TiddlyWeb.extend(TiddlyWeb.Bag, TiddlyWeb.Resource);

//Tiddlers
TiddlyWeb.Tiddlers = function(container_type, container_name) {
    TiddlyWeb.Tiddlers.baseConstructor.call(this);
    this.container_type = container_type;
    this.container_name = container_name;
}

TiddlyWeb.extend(TiddlyWeb.Tiddlers, TiddlyWeb.Resource);

//RecipeTiddlers
TiddlyWeb.RecipeTiddlers = function(container) {
    TiddlyWeb.RecipeTiddlers.baseConstructor.call(this, 'recipes', container);
    this.type = 'recipe_tiddlers';
}

TiddlyWeb.extend(TiddlyWeb.RecipeTiddlers, TiddlyWeb.Tiddlers);

//BagTiddlers
TiddlyWeb.BagTiddlers = function(container) {
    TiddlyWeb.BagTiddlers.baseConstructor.call(this, 'bags', container);
    this.type = 'bag_tiddlers';
}

TiddlyWeb.extend(TiddlyWeb.BagTiddlers, TiddlyWeb.Tiddlers);

//Tiddler
TiddlyWeb.Tiddler = function(container_type, container_name, title) {
    TiddlyWeb.Tiddler.baseConstructor.call(this);
    this.container_type = container_type;
    this.container_name = container_name;
    this.type = 'tiddler';
    this.title = title;
}

TiddlyWeb.extend(TiddlyWeb.Tiddler, TiddlyWeb.Resource);

//BagTiddler
TiddlyWeb.BagTiddler = function(bag_name, title) {
    TiddlyWeb.BagTiddler.baseConstructor.call(this, 'bags', bag_name, title);
}

TiddlyWeb.extend(TiddlyWeb.BagTiddler, TiddlyWeb.Tiddler);

//RecipeTiddler
TiddlyWeb.RecipeTiddler = function(recipe_name, title) {
    TiddlyWeb.RecipeTiddler.baseConstructor.call(this, 'recipes', recipe_name, title);
}

TiddlyWeb.extend(TiddlyWeb.RecipeTiddler, TiddlyWeb.Tiddler);

//TiddlerRevisions
TiddlyWeb.TiddlerRevisions = function(container_type, container_name, title) {
    TiddlyWeb.TiddlerRevisions.baseConstructor.call(this, container_type, container_name);
    this.title = title;
}

TiddlyWeb.extend(TiddlyWeb.TiddlerRevisions, TiddlyWeb.Tiddlers);

TiddlyWeb.TiddlerRevisions.prototype.presenter = function() {
    $(this.container_id).append('<p>' + this.type + ': ' +
            $.map(this.data, function(n)
                {return n.title + ':' + n.revision}).join(', ') + '</p>');
}

//TiddlerBagRevisions
TiddlyWeb.BagTiddlerRevisions = function(bag_name, title) {
    TiddlyWeb.BagTiddlerRevisions.baseConstructor.call(this, 'bags', bag_name, title);
    this.type = 'bag_tiddler_revisions';
}

TiddlyWeb.extend(TiddlyWeb.BagTiddlerRevisions, TiddlyWeb.TiddlerRevisions);

//TiddlerRecipeRevisions
TiddlyWeb.RecipeTiddlerRevisions = function(recipe_name, title) {
    TiddlyWeb.RecipeTiddlerRevisions.baseConstructor.call(this, 'recipes', recipe_name, title);
    this.type = 'recipe_tiddler_revisions';
}

TiddlyWeb.extend(TiddlyWeb.RecipeTiddlerRevisions, TiddlyWeb.TiddlerRevisions);

function main() {
    recipes = new TiddlyWeb.Recipes();
    recipes.get(1);
    bags = new TiddlyWeb.Bags();
    bags.container_id = '#bag';
    bags.get(1);
    bag = new TiddlyWeb.Bag('system');
    bag.container_id = '#bag';
    bag.get(1);
    bag_tiddlers = new TiddlyWeb.BagTiddlers('system');
    bag_tiddlers.container_id = '#bag';
    bag_tiddlers.get(1);
    recipe_tiddlers = new TiddlyWeb.RecipeTiddlers('default');
    recipe_tiddlers.get(1);
    tiddler = new TiddlyWeb.BagTiddler('system', 'TiddlyWebAdaptor');
    tiddler.container_id = '#bag';
    tiddler.get(1);
    revisions = new TiddlyWeb.BagTiddlerRevisions('system', 'TiddlyWebAdaptor');
    revisions.container_id = '#bag';
    revisions.get(1);
    revisions = new TiddlyWeb.RecipeTiddlerRevisions('default', 'TiddlyWebAdaptor');
    revisions.get(1);
}
