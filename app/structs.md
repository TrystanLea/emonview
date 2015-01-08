    // nearest to the present form, requires concept of var id
    // - difficult to address
    var rxkeys = [
        {"name": "nodes/emontx/power1", "value":250, "time":0, "units":"W"},
        {"name": "nodes/emontx/power2", "value":250, "time":0, "units":"W"},
        {"name": "nodes/emontx/power3", "value":250, "time":0, "units":"W"}
    ];
    
    // A better implementation that enforces a unique var name
    // + can use redis hget hset
    // - mqtt has no hget
    // + easy to select key
    var rxkeys = {
        "nodes/emontx/power1":{"value":250, "time":0, "units":"W"},
        "nodes/emontx/power2":{"value":250, "time":0, "units":"W"},
        "nodes/emontx/power3":{"value":250, "time":0, "units":"W"}
    };
    
    // Every property has its own full name key
    // - verbose, very extensive key list, could this be slower?
    // + easier to turn directly into a http api
    // + easier to turn directly into a dom key
    // - harder to compile at initial view but maybe only slightly
    var rxkeys = {
        "nodes/emontx/power1/value":250,
        "nodes/emontx/power1/time":0,
        "nodes/emontx/power1/units":"W",
        
        "nodes/emontx/power2/value":150,
        "nodes/emontx/power2/time":0,
        "nodes/emontx/power2/units":"W",
        
        "nodes/emontx/power3/value":250,
        "nodes/emontx/power3/time":0,
        "nodes/emontx/power3/units":"W",
        
        "nodes/emonth/temperature/value":18.5,
        "nodes/emonth/temperature/time":0,
        "nodes/emonth/temperature/units":"C",
        
        "nodes/emonth/battery/value":3.3,
        "nodes/emonth/battery/time":0,
        "nodes/emonth/battery/units":"V"
    };
    
    var nodes = {};
    for (key in rxkeys)
    {
        var keyparts = key.split("/");
        
        if (keyparts[0] == "nodes") {
            var nodename = keyparts[1]; var varname = keyparts[2];
            if (nodes[nodename]==undefined) nodes[nodename] = [];  
            if (nodes[nodename].indexOf(varname)==-1) nodes[nodename].push(varname);  
        }
    }
    
    // nodes = {"emontx":["power1","power2","power3"]};
    
    for (nodename in nodes)
    {
        var out = "";
        for (i in nodes[nodename]) {
            varname = nodes[nodename][i];
            var valuekey = "nodes/"+nodename+"/"+varname+"/value";
            var unitskey = "nodes/"+nodename+"/"+varname+"/units";
            out += "<tr><td>"+varname+"</td><td><span key='"+valuekey+"'></span> <span key='"+unitskey+"'></span></td></tr>";
        }
        $("#nodelist").append('<li><a href="#nodes/'+nodename+'">'+nodename+'</a></li>');
        $("#variable-table").append("<tbody node='"+nodename+"' style='display:none'>"+out+"</tbody>");
    }
    
    
    // Set all keys
    for (key in rxkeys) $('[key="'+key+'"]').html(rxkeys[key]);
    $("#emontx-vars").show();
    
    // hierarchy - nice but gets quite complicated to work with, difficult to update individual nodes in nodes store if key is base nodes
    // - makes little use of key:value store features without storing entire object as value.
    // + in form thats readily selectable in the app, good for initial display drawing
    var rxkeys = {
        "nodes":{
            "emontx":{
                "power1":{"value":250, "time":0, "units":"W"},
                "power2":{"value":250, "time":0, "units":"W"},
                "power3":{"value":250, "time":0, "units":"W"}
            }
        }
    };
    
    
    
    
    
    
    =================
    
    
        var nodes = {};
    for (key in rxkeys)
    {
        var keyparts = key.split("/");
        
        if (keyparts[0] == "rx") {
            var nodename = keyparts[1]; var varname = keyparts[2];
            if (nodes[nodename]==undefined) nodes[nodename] = [];  
            if (nodes[nodename].indexOf(varname)==-1) nodes[nodename].push(varname);  
        }
    }
    
    for (nodename in nodes)
    {
        var out = "";
        for (i in nodes[nodename]) {
            varname = nodes[nodename][i];
            var valuekey = "rx/"+nodename+"/"+varname+"/value";
            var unitskey = "rx/"+nodename+"/"+varname+"/units";
            out += "<tr><td>"+varname+"</td><td><span key='"+valuekey+"'></span> <span key='"+unitskey+"'></span></td></tr>";
        }
        $("#nodelist").append('<li><a href="#nodes/'+nodename+'">'+nodename+'</a></li>');
        $("#variable-table").append("<tbody node='"+nodename+"' style='display:none'>"+out+"</tbody>");
    }
