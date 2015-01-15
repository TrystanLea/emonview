var viskey = "";
var loadedhistoric = "";
var data = {};
var graphdata = [];

var options = {
    lines: { show:true, fill: false },
    points: { show:false},
    xaxis: { mode: "time", timezone: "browser", minTickSize: [1, "second"]}, // 
    // yaxis: { min: 0 },
    grid: {hoverable: true, clickable: true},
    selection: { mode: "x" }
};
    
function show_node(nodename)
{
    $("#variable-table tbody").hide();
    $("[node="+nodename+"]").show();
    $('li').removeClass("selected");
    $('a[href="#nodes/'+nodename+'"]').parent().addClass("selected");
}

function draw_nodes()
{
    $("#nodelist").html("");
    $("#variable-table").html("");
    for (nodeid in nodes)
    {
        var node = nodes[nodeid];
        var nodename = node['nodename'];
        $("#nodelist").append('<li><a href="#nodes/'+nodename+'">'+nodename+'</a></li>');
        $("#variable-table").append("<tbody node='"+nodename+"' style='display:none'></tbody>");

        if (node['Rx']!=undefined && node['Tx']!=undefined) $('tbody[node="'+nodename+'"]').append("<tr><th>Rx</td><td></td></tr>");        

        if (node['Rx']!=undefined) draw_variables(node['Rx'],nodename,'rx');
        
        if (node['Rx']!=undefined && node['Tx']!=undefined) $('tbody[node="'+nodename+'"]').append("<tr><th>Tx</td><td></td></tr>");  
        
        if (node['Tx']!=undefined) draw_variables(node['Tx'],nodename,'tx');      
    }
}

function draw_variables(packet,nodename,mode)
{
    var names = packet['names'];
    var units = []; if (packet['units']!=undefined) units = packet['units'];
    var values = []; if (packet['values']!=undefined) values = packet['values'];
    for (vid in names)
    {
        var varname = names[vid];
        var unit = ""; if (units[vid]!=undefined) unit = units[vid];
         
        var valuekey = mode+"/"+nodename+"/"+varname+"/value";
        var unitskey = mode+"/"+nodename+"/"+varname+"/units";
        var out = "<tr class='vis clickable' viskey='"+valuekey+"'><td>"+varname+"</td><td><span key='"+valuekey+"'>"+values[vid]+"</span> "+unit+"</td></tr>";
        $('tbody[node="'+nodename+'"]').append(out);
    } 
}

function load_nodes()
{
    $.ajax({ type:'GET', url: "api/nodes", dataType: 'json', async:true, success: function(data){
        nodes = data;
        draw_nodes();
    }});
}

//===============================================================================================

function history_graph(viskey)
{
    var keyparts = viskey.split("/");
    var nodename = keyparts[1]; var varname = keyparts[2];
    
    // end = (new Date()).getTime();
    end = appstart;
    start = end - 3600*1000;
    interval = 5;
    
    $.ajax({
        url: 'data/'+nodename+'/'+varname+'?start='+start+'&end='+end+'&interval='+interval,
        dataType: 'json',
        async: false,
        success: function(result) { 
            graphdata = result;
            graphdata.push(data[viskey][0]);
            loadedhistoric = viskey;
            plot();
            
        }
    });
}

function plot()
{
    var series = [];
    if (loadedhistoric==viskey) series.push({data:graphdata, color:"#edc241"});
    series.push({data:data[viskey], color:"#f1a748"});

    $.plot("#placeholder",series,options);
}
