
// play with jquery and chrjs

function manage_list_resource(element) {
    var resource = $(element).prev().attr("class").split(' ')[1];
    var collection = new TiddlyWeb.Collection(resource, "");
    collection.get(function(data){
        var list = $(element).children('ul');
        list.empty(); // why not chain this?
        $.each(data, function(i, item){
            list.append('<li><p>' + item + '</p><p></p></li>');
        });
        list.find("li").click(function(event) {
            $(this).find('p:last').toggle("fast", function() {
                if($(this).is(":visible")) {
                    manage_resource(this, resource);
                }
            });
        });
    });
}

function manage_resource(element, parent_resource) {
    var resource = parent_resource.charAt(0).toUpperCase() +
        parent_resource.substr(1);
    resource = resource.replace(/s$/, '');
    var name = $(element).prev().text();
    var thing = new TiddlyWeb[resource](name, "");
    thing.get(function(data){
        $(element).empty().
            html('desc: ' + data.desc + '<br/><a href="">Tiddlers</a>' + '<ul></ul>').
            find('a').click(function(event){
                $(element).find('ul').toggle("fast", function(){
                    if($(this).is(":visible")) {
                        get_tiddlers(this, element, thing);
                    }
            });
            event.preventDefault();
            event.stopPropagation();
        });
    });
}

function get_tiddlers(link, where, thing) {
    thing.tiddlers().get(function(data){
        var list = $(where).find('ul');
        list.empty();
        $.each(data, function(i, item){
            // do more here
            list.append('<li>' + item.title + '</li>');
        });
    }
    );
}

function elmo_init() {
    $("#meat").click(function(event){
        event.preventDefault();
        $(this).replaceWith($("#resource").show());
    });

    $("#resource .data").click(function(event){
        $(this).next().toggle("fast", function() {
            if ($(this).is(":visible")) {
                manage_list_resource(this);
            }
        });
    });

    $("#msg").click(function(event){
        $(this).html("No current messages.");
    });
}
