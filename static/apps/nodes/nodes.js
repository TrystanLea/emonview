
var app_nodes = {
    // note variable nodes is global!

    selected_node: 0,
    updater: false,

    init: function()
    {
        console.log(path);
        
        $.ajax({ 
            url: path+"api", 
            dataType: 'json', 
            async: true, 
            success: function(data) {
                nodes = data;
                // auto select first node
                for (var key in nodes) {
                    app_nodes.selected_node = key;
                    break;
                }
            }
        });

        $("#node-nav").on("click","li",function() {
            var nid = $(this).attr("nid");
            app_nodes.selected_node = nid;
            $(".node").hide();
            $(".node[nid="+nid+"]").show();
        });
        
        $(document).on("socketio_msg",function( event, msg ) {
            var topic = msg.topic.split("/");
            var values = msg.payload.split(",");
            
            if (topic[0]=="api" && topic[2]=="values") {
                var nodeid = topic[1];
                if (nodes[nodeid]==undefined) nodes[nodeid] = {};
                nodes[nodeid].time = (new Date()).getTime()/1000;
                nodes[nodeid].values = values;
            }
        });    
    },
    
    show: function()
    {
        app_nodes.draw_nodes();
        app_nodes.updater = setInterval(app_nodes.update,1000);
    },
    
    hide: function()
    {
        clearInterval(app_nodes.updater);
    },

    draw_nodes: function ()
    {
        $("#node-nav").html("");
        $("#node-content").html("");
        var template_node = $("#template-node").html();
        var template_variable = $("#template-variable").html();
        
        for (z in nodes)
        {
            // node entry in left hand side navigation list
            $("#node-nav").append("<li nid="+z+"><a>"+z+": "+nodes[z].nodename+"</a></li>");
            
            // make a copy of node info & variables block template, set its nodeid
            var display = "";
            if (app_nodes.selected_node!=z) display = "display:none";
            $("#node-content").append("<div class='node' nid="+z+" style='"+display+"'>"+template_node+"</div>");
            
            // select the copied block
            var node = $(".node[nid="+z+"]");
            node.find(".node-id").html(z);              // set the nodeid
            node.find(".node-key").html(nodes[z].nodename);
            node.find(".node-firmware").html(nodes[z].firmware);
            node.find(".node-hardware").html(nodes[z].hardware);
            
            if (nodes[z].time==undefined) nodes[z].time = 0;
            
            if (nodes[z].names==undefined) nodes[z].names = [];
            if (nodes[z].values==undefined) nodes[z].values = [];
            if (nodes[z].units==undefined) nodes[z].units = [];
            
            var varnum = 0;
            if (nodes[z].names.length>varnum) varnum = nodes[z].names.length;
            if (nodes[z].values.length>varnum) varnum = nodes[z].values.length;
            if (nodes[z].units.length>varnum) varnum = nodes[z].units.length;
            
            for (var v=0; v<varnum; v++) {
                if (nodes[z].names[v]==undefined) nodes[z].names[v] = "";
                if (nodes[z].values[v]==undefined) nodes[z].values[v] = "0.0";
                if (nodes[z].units[v]==undefined) nodes[z].units[v] = "";
            }
            
            var variables = "";
            for (var v=0; v<varnum; v++) {
                variables += "<tr vid="+v+">"+template_variable+"</tr>";
            }
            node.find(".variables").html(variables);
                
            for (var v=0; v<varnum; v++) {
                var row = node.find("tr[vid="+v+"]");
                row.find("td[key=variable-id]").html(v);
                if (nodes[z].names) row.find("td[key=variable-name]").html(nodes[z].names[v]);
                if (nodes[z].values) row.find("span[key=variable-value]").html(nodes[z].values[v]);
                if (nodes[z].units) row.find("span[key=variable-unit]").html(nodes[z].units[v]);
                row.find("td[key=variable-time]").html(app_nodes.list_format_updated(nodes[z].time));
                
                if (nodes[z].record!=undefined && parseInt(nodes[z].record[v])>0) {
                    var view = row.find("a[key=view]");
                    view.show();
                    view.attr("href","#graph/"+z+"/"+v);
                    view.find(".interval").html(nodes[z].record[v]+"s");
                }
            }
        }
    },

    update: function ()
    {
        /*
        $.ajax({ 
            url: path+"api", 
            dataType: 'json', 
            async: true, 
            success: function(data) {
                nodes = data;
                app_nodes.draw_nodes();
            }
        });
        */
        app_nodes.draw_nodes();
    },

    list_format_updated: function (time)
    {
      time = time * 1000;
      var now = (new Date()).getTime();
      var update = (new Date(time)).getTime();
      var lastupdate = (now-update)/1000;

      var secs = (now-update)/1000;
      var mins = secs/60;
      var hour = secs/3600

      var updated = secs.toFixed(0)+"s ago";
      if (secs>180) updated = mins.toFixed(0)+" mins ago";
      if (secs>(3600*2)) updated = hour.toFixed(0)+" hours ago";
      if (hour>24) updated = "inactive";

      var color = "rgb(255,125,20)";
      if (secs<25) color = "rgb(50,200,50)"
      else if (secs<60) color = "rgb(240,180,20)"; 

      return "<span style='color:"+color+";'>"+updated+"</span>";
    }
}
