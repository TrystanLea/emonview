var graph = {

    element: false,
    ctx: false,
    
    // Pixel width and height of graph
    width: 200,
    height: 200,
    
    
    draw: function(element,series) {
        // Initialise the canvas get context
        if (!ctx) 
        {
            this.element = element;
            var c = document.getElementById(element);  
            this.ctx = c.getContext("2d");
        }
        
        var ctx = this.ctx;
        
        ctx.beginPath();
        ctx.closePath();
        ctx.stroke();
        
        // Clear canvas
        ctx.clearRect(0,0,this.width,this.height);
        
        // OEM Blue
        ctx.strokeStyle = "#0699fa";
        ctx.fillStyle = "#0699fa";
        
        // Axes
        ctx.moveTo(0,0);
        ctx.lineTo(0,this.height);
        ctx.lineTo(this.width,this.height);
        ctx.stroke();
        
        // find out max and min values of data
        
        var xmin = undefined;
        var xmax = undefined;
        var ymin = undefined;
        var ymax = undefined;
        
        for (s in series)
        {
            var data = series[s];
            for (z in data)
            {
                if (xmin==undefined) xmin = data[z][0];
                if (xmax==undefined) xmax = data[z][0];
                if (ymin==undefined) ymin = data[z][1];
                if (ymax==undefined) ymax = data[z][1];
                            
                if (data[z][1]>ymax) ymax = data[z][1];
                if (data[z][1]<ymin) ymin = data[z][1];
                if (data[z][0]>xmax) xmax = data[z][0];
                if (data[z][0]<xmin) xmin = data[z][0];               
            }
        }
       
        
        var r = (ymax - ymin);
        ymin = (ymin + (r / 2)) - (r/1.5);
        ymax = (ymax - (r / 2)) + (r/1.5);
        
        var scale = 1;
        
        s=0;
        ctx.beginPath()
        var data = series[s];
        for (z in data)
        {
            var x = ((data[z][0] - xmin) / (xmax - xmin)) * this.width;
            var y = this.height - (((data[z][1] - ymin) / (ymax - ymin)) * this.height);
            if (z==0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
            
            ctx.fillRect(x-2,y-2,4,4);
        }
        ctx.stroke();
    }

};
