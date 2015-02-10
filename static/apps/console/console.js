var app_console = {

    init: function()
    {
        $(document).on("socketio_msg",function( event, msg ) {
            $(".console-out").append(msg.topic+" "+msg.payload+"\n");
            var h = parseInt($('#log')[0].scrollHeight);
            $('#log').scrollTop(h);
        });
    },
    
    show: function()
    {
    
    },
    
    hide: function()
    {
    
    }
}
