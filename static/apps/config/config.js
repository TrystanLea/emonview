var app_config = {

    init: function()
    {
        $("#saveconf").click(function(){
        
            $.ajax({ 
                type:'POST', 
                url: "conf", 
                contentType: "text/plain", 
                data: $("#emonhubconf").val(),
                success: function(data) {
                
                    $.ajax({ 
                        url: path+"api", 
                        dataType: 'json', 
                        async: true, 
                        success: function(data) {
                            nodes = data;
                            app_nodes.update();
                        }
                    });
                }
            });
        });
    },
    
    show: function()
    {
        $.ajax({ url: "conf", cache: false, success: function(data){
            $("#emonhubconf").val(data);
        }});
    },
    
    hide: function()
    {
    
    }
}
