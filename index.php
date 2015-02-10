<?php

/*

Licence: GPL Affero

This PHP version has not yet been updated to match the server.py implementation
The intention is to have both implementations available

*/

error_reporting(E_ALL);
ini_set('display_errors', 'on');

$redis = new Redis();
$connected = $redis->connect("127.0.0.1");


// require "Lib/PHPFina.php";
// $phpfina = new PHPFina("/home/pi/data/phpfina2/");

$url = $_GET['q'];
$url = explode("/",$url);

$action = $url[0];
$method = $_SERVER['REQUEST_METHOD'];
    
if ($action=='client') {
    print file_get_contents("client.html");
    die;
}

if ($action=="bulk")
{
    $data = json_decode($_POST['data']);
    $time_ref = time() - (int) $_POST['sentat'];
    
    foreach ($data as $item)
    {
        $itemtime = (int) $item[0];
        $time = $time_ref + (int) $itemtime;
        $nodeid = $item[1];
        $values = array_slice($item,2);
        
        $nodes = json_decode($redis->get("nodes"));
        if (!isset($nodes->$nodeid)) $nodes->$nodeid = new stdClass;
        $nodes->$nodeid->time = $time;
        $nodes->$nodeid->values = $values;
        $redis->set("nodes",json_encode($nodes));
        
        $varid = 0;
        foreach ($values as $value) {
            store($nodeid,$varid,$time,$value);
            $varid ++;
        }
    }
    
    $result = "ok";
}
else
{
    $input = false;
    
    $input = file_get_contents('php://input');
    if (isset($_GET['val'])) $input = $_GET['val'];
    
    $nodeid = false;
    $varid = false;
    $prop = false;
    
    if (isset($url[1]) && is_numeric($url[1])) $nodeid = $url[1];
    if (isset($url[2]) && is_numeric($url[2])) $varid = $url[2];
    if ($nodeid==false && $varid===false && isset($url[1])) $prop = $url[1];
    if ($nodeid!==false && $varid===false && isset($url[2])) $prop = $url[2];
    if ($nodeid!==false && $varid!==false && isset($url[3])) $prop = $url[3];
    
    // POST NODE
    // Implemented:
    // - set all /config
    //
    // - /set/12/values
    // - /set/12/nodename
    // - /set/12/hardware etc
    //
    // - /set/12/0/name
    // - /set/12/0/unit
    
    if ($method =="POST") {
    
        if ($nodeid===false && $varid===false && $prop!==false) 
        {
            if ($prop=="config") $redis->set("config",$input);
        }

        if ($nodeid!==false && $varid===false && $prop!==false) 
        {
            if ($prop=="values") {
                $time = time();
                $values = explode(",",$input);
                
                $nodes = json_decode($redis->get("nodes"));
                if (!isset($nodes->$nodeid)) $nodes->$nodeid = new stdClass;
                $nodes->$nodeid->time = $time;
                $nodes->$nodeid->values = $values;
                $redis->set("nodes",json_encode($nodes));
                
                $varid = 0;
                foreach ($values as $value) {
                    store($nodeid,$varid,$time,$value);
                    $varid ++;
                }                        
            } else {
                $config = json_decode($redis->get("config")); 
                if ($config==null) $config = new stdClass;
                if (!isset($config->$nodeid)) $config->$nodeid = new stdClass;
                if ($prop=="nodename") $config->$nodeid->nodename = $input;
                if ($prop=="hardware") $config->$nodeid->hardware = $input;
                if ($prop=="firmware") $config->$nodeid->firmware = $input;
                if ($prop=="names") $config->$nodeid->names = explode(",",$input);
                if ($prop=="units") $config->$nodeid->units = explode(",",$input);
                $redis->set("config",json_encode($config));
                $result = $config;
            }
        }
        
        if ($nodeid!==false && $varid!==false && $prop!==false) 
        {
            $config = json_decode($redis->get("config")); 
            if ($config==null) $config = new stdClass;
            if (!isset($config->$nodeid)) $config->$nodeid = new stdClass;
            
            if ($prop=="name") $config->$nodeid->names[$varid] = $input;
            if ($prop=="unit") $config->$nodeid->units[$varid] = $input;
            
            $redis->set("config",json_encode($config));
            $result = $config;
        }
    }
    
    // -------------------------------------------------------------------------
    // METHOD: GET
    // -------------------------------------------------------------------------
    if ($method == "GET")
    {
    
        $config = json_decode($redis->get("config"));
        $nodes = json_decode($redis->get("nodes"));
        // GET ALL
        // returns full list of nodes with configuration
        if ($nodeid===false && $varid===false && $prop===false) 
        {
            foreach ($config as $id=>$node) {
                foreach ($node as $key=>$prop) {
                   $nodes->$id->$key = $prop;
                }
            }
            $result = $nodes;
        }

        // GET NODE
        // returns json object with all node properties for requested node
        if ($nodeid!==false && $varid===false && $prop===false) 
        {
            $node = $config->$nodeid;
            $node->time = $nodes->$nodeid->time;
            $node->values = $nodes->$nodeid->values;
            $result = $node;
        }
        
        // returns only requested property of requested node
        if ($nodeid!==false && $varid===false && $prop!==false) 
        {
            if ($prop=="nodename") $result = $config->$nodeid->nodename;
            if ($prop=="firmware") $result = $config->$nodeid->firmware;
            if ($prop=="hardware") $result = $config->$nodeid->hardware;
            if ($prop=="names") $result = $config->$nodeid->names;
            if ($prop=="units") $result = $config->$nodeid->units;
            if ($prop=="values") $result = $nodes->$nodeid->values;
        }
        
        // GET NODE:VAR
        if ($nodeid!==false && $varid!==false && $prop===false)
        {
            $result = array(
                "name"=>$config->$nodeid->names[$varid],
                "value"=>$nodes->$nodeid->values[$varid],
                "unit"=>$config->$nodeid->units[$varid]
            );
        }
        
        if ($nodeid!==false && $varid!==false && $prop!==false)
        {
            
            if ($prop=="name") $result = $config->$nodeid->names[$varid];
            if ($prop=="unit") $result = $config->$nodeid->units[$varid];
            if ($prop=="value") $result = $nodes->$nodeid->values[$varid];
            
            if ($prop == "meta") {
                $name = $nodeid."_".$varid;
                $meta = $phpfina->get_meta($name);
                
                $result = array(
                    "start"=>$meta->start_time,
                    "interval"=>$meta->interval,
                    "npoints"=>$phpfina->get_npoints($name),
                    "size"=>$phpfina->get_size($name)
                );
            }
        
            if ($prop == "data") {
                $name = $nodeid."_".$varid;
                $start = $_GET['start'];
                $end = $_GET['end'];
                $interval = (int) $_GET['interval'];
                
                $result = $phpfina->get_data($name,$start,$end,$interval);
            }
        }
    }
}

header('Content-Type: application/json');

$type = gettype($result);

if ($type=="array" || $type=="object") {
    print json_encode($result, JSON_PRETTY_PRINT);
} else {
    print $result;
}

function store($nodeid,$varid,$time,$value)
{
    /*
    $name = $nodeid."_".$varid;
    $result = $phpfina->prepare($name,$time,$value);

    // Auto create feed if it does not exist
    if ($result===false) {
        if (!$phpfina->get_meta($name)) {
            $phpfina->create($name,10);
            $result = $phpfina->prepare($name,time(),$value);
        }
    }

    if ($result!==false) $phpfina->save();
    */
}
