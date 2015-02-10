## API

### GET /api
	
GET /api

    {
        "10":{
            "nodename":"House",
            "firmware":"emontx_firmware_continuous",
            "hardware":"EmonTx v3.4",
            "time":1423344776,
            "names":["power1","power2","power3"],
            "values":["100","200","300"],
            "units":["W","W","W"]
        }
    }

### GET nodes/nodeid

GET /api/10

    {
        "nodename":"House",
        "firmware":"emontx_firmware_continuous",
        "hardware":"EmonTx v3.4",
        "time":1423344776,
        "names":["power1","power2","power3"],
        "values":["100","200","300"],
        "units":["W","W","W"]
    }

GET /api/10/nodename

    "House"

GET /api/10/hardware

    "EmonTx v3.4"

GET /api/10/firmware

"emontx_firmware_continuous"

GET /api/10/names

    ["power1","power2","power3"]

GET /api/10/values

    [100,200,300]

GET /api/10/units

    ["W","W","W"]

### GET nodes/nodeid/varid

GET /api/10/0

    {"name":"power1","value":"100","unit":"W"}

GET /api/10/0/name

    "power1"

GET /api/10/0/value

    100

GET /api/10/0/unit

    "W"

GET /api/10/0/meta

    {"start":null,"interval":null,"npoints":0,"size":false}

GET /api/10/0/data?start=0&end=0&interval=60

    timeseries data

### POST

Data is placed in request body with contentType "text/plain" apart from /api/bulk.

### POST nodes
	
POST /api/config

    {
        "10":{
            "nodename":"House",
            "firmware":"emontx_firmware_continuous",
            "hardware":"EmonTx v3.4",
            "names":["power1","power2","power3"],
            "units":["W","W","W"]
        }
    }
     
POST /api/bulk (contentType: application/x-www-form-urlencoded)

    data=[[0,10,110,200,300],[10,10,120,200,290],[15,10,130,200,280]]&sentat=20
    
### POST nodes/nodeid
	
POST /api/10/values

    100,200,300

POST /api/10/nodename

    House

POST /api/10/hardware

    EmonTx v3.4
    
POST /api/10/firmware

    emontx_firmware_continuous
    
POST /api/10/names

    power1,power2,power3
    
POST /api/10/units

    W,W,W
    
### POST nodes/nodeid/varid	

POST /api/10/0/name

    power1

POST /api/10/0/unit

    W	

