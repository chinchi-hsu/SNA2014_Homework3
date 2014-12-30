<?php
include("database_info.php");
include("node_convertion.php");

// ==== Connect to the database ====
$database = new mysqli($databaseURL, $databaseAccount, $databasePassword, $databaseName);
if($database -> connect_error){
    die("No connection to the team table");
}





// ==== Check if the team is legal or not ====
if(!isset($_GET["team"])){
    storeQueryString(0);
    die("No team id!");   
}
$teamQuery = $_GET["team"];

$statement = $database -> prepare("SELECT team_id, prime_key FROM " . $teamTableName . " WHERE password = ?");
$statement -> bind_param("s", $teamQuery);
$statement -> execute();
$team = NULL;
$primeKey = NULL;
$statement -> bind_result($team, $primeKey);       // The team id will be stored in $team if the team query is legal
if(!$statement -> fetch()){
    storeQueryString(0);
    die("The team does not exist!");
}
$statement -> close();





// ==== Check if the network is legal or not ====
if(!isset($_GET["network"])){
    /*
    storeQueryString(0);
    die("No network id!");
    */
}
$_GET["network"] = "23392036";         # reads default network id 1
$networkQuery = (int)$_GET["network"];

$statement = $database -> prepare("SELECT network_id, node_type_count, edge_type_count FROM " . $networkTableName . " WHERE network_id = ?");
$statement -> bind_param("i", $networkQuery);
$statement -> execute();
$network = NULL;
$nodeTypeCount = NULL;
$edgeTypeCount = NULL;
$statement -> bind_result($network, $nodeTypeCount, $edgeTypeCount);    // The network id will be stored in $network if the network query is legal
if(!$statement -> fetch()){
    storeQueryString(0);
    die("The network does not exist!");
}
$statement -> close();





// ==== Store the query string ====
function storeQueryString($team){
    $database = $GLOBALS["database"];
    $logTableName = $GLOBALS["logTableName"];
    $queryString = (isset($_SERVER["QUERY_STRING"])) ? $_SERVER["QUERY_STRING"] : ""; 

    $statement = $database -> prepare("INSERT INTO " . $logTableName . " (team_id, query_string, query_time) VALUES (?, ?, NOW())");
    $statement -> bind_param("is", $team, $queryString);
    $statement -> execute();
    $statement -> close();
}
storeQueryString($team);





// ==== Check if the node is legal or not ====
if(!isset($_GET["node"])){
    $queryCountNetwork = $network;
    if($fakeNetworkEnabled){
        $queryCountNetwork = $fakeNetwork;
    }
    $queryCount = getQueryCount($team, $queryCountNetwork);
    showTeamInformation($team, $queryCount);
    echo($nodeTypeCount . " " . $edgeTypeCount . "\n");

    // Read edges from the seed file
    $nodeSet = array();
    $edgeSet = array();
    $seedFile = fopen("seed.txt", "r");    # seed file path
    $node1 = NULL;
    $node2 = NULL;
    while(fscanf($seedFile, "%d%d", $node1, $node2) == 2){
        $nodeSet[$node1] = 0;
        $nodeSet[$node2] = 0;

        $nodeFrom = min($node1, $node2);
        $nodeTo = max($node1, $node2);
        if(!array_key_exists($nodeFrom, $edgeSet)){
            $edgeSet[$nodeFrom] = array();
        }
        $edgeSet[$nodeFrom][$nodeTo] = 0;
    }
    fclose($seedFile);

    // Print nodes and edges
    ksort($nodeSet);
    ksort($edgeSet);
    echo(count($nodeSet) . "\n");
    foreach($nodeSet as $node => $value){
        showNodeInformation($network, $node, $primeKey, $nodeTypeCount); 
    }
    foreach($edgeSet as $nodeFrom => $nodeToSet){
        foreach($nodeToSet as $nodeTo => $value){
            showEdgeInformation($network, $nodeFrom, $nodeTo, $primeKey, $edgeTypeCount);
        }
    }

    exit();
}
$nodeQuery = (int)$_GET["node"];





// ==== Retrieve the neighbors of the node ====
function getNodeTypes($network, $node, $nodeTypeCount){
    $database = $GLOBALS["database"];
    $nodeTableName = $GLOBALS["nodeTableName"];
    
    $nodeTypes = array();
    for($i = 1; $i <= $nodeTypeCount; $i ++){
        $statement = $database -> prepare("SELECT node_type_" . $i . " FROM ". $nodeTableName . " WHERE network_id = ? AND node = ?");
        $statement -> bind_param("ii", $network, $node);
        $statement -> execute();
        $nodeType = NULL;
        $statement -> bind_result($nodeType);
        if($statement -> fetch()){
            array_push($nodeTypes, $nodeType);    
        }
        $statement -> close();
    }

    return $nodeTypes;
}
function getEdgeTypes($network, $nodeFrom, $nodeTo, $edgeTypeCount){
    $database = $GLOBALS["database"];
    $edgeTableName = $GLOBALS["edgeTableName"];

    $edgeTypes = array();
    for($i = 1; $i <= $edgeTypeCount; $i ++){
        $statement = $database -> prepare("SELECT edge_type_" . $i . " FROM ". $edgeTableName . " WHERE network_id = ? AND node_from = ? AND node_to = ?");
        $statement -> bind_param("iii", $network, $nodeFrom, $nodeTo);
        $statement -> execute();
        $edgeType = NULL;
        $statement -> bind_result($edgeType);
        if($statement -> fetch()){
            array_push($edgeTypes, $edgeType);
        }
        $statement -> close();
        
        $statement = $database -> prepare("SELECT edge_type_" . $i . " FROM ". $edgeTableName . " WHERE network_id = ? AND node_from = ? AND node_to = ?");
        $statement -> bind_param("iii", $network, $nodeTo, $nodeFrom);
        $statement -> execute();
        $edgeType = NULL;
        $statement -> bind_result($edgeType);
        if($statement -> fetch()){
            array_push($edgeTypes, $edgeType);
        }
        $statement -> close();
    }
    return $edgeTypes;
}
function getNodeDegree($network, $node){
    $database = $GLOBALS["database"];
    $nodeTableName = $GLOBALS["nodeTableName"];

    $statement = $database -> prepare("SELECT degree FROM " . $nodeTableName . " WHERE network_id = ? AND node = ?");
    $statement -> bind_param("ii", $network, $node);
    $statement -> execute();
    $degree = NULL;
    $statement -> bind_result($degree);
    $statement -> fetch();
    $statement -> close();
    return $degree;
}
function getNodeNeighbors($network, $node){
    $database = $GLOBALS["database"];
    $nodeTableName = $GLOBALS["nodeTableName"];
    $edgeTableName = $GLOBALS["edgeTableName"];

    $statement = $database -> prepare("SELECT neighbors FROM " . $nodeTableName . " WHERE network_id = ? AND node = ?");
    $statement -> bind_param("ii", $network, $node);
    $statement -> execute();
    $neighborWord = NULL;
    $statement -> bind_result($neighborWord);
    $statement -> fetch();
    $statement -> close();

    $neighborSet = array();
    $neighborStrings = explode(",", $neighborWord);
    if(count($neighborStrings) == 1 && $neighborStrings[0] == ""){
        $neighborStrings = array();     // clear the string array without neighbor information
    }
    foreach($neighborStrings as $neighborStr){
        $neighborSet[(int)$neighborStr] = 0;
    }
    return array_keys($neighborSet);
}
if($nodeEncodingEnabled){
    $node = convertNodeID($nodeQuery, $primeKey);
}
else{
    $node = $nodeQuery;
}
$neighbors = getNodeNeighbors($network, $node);





// ==== Count and increment the query frequency ====
function getQueryCount($team, $network){
    $database = $GLOBALS["database"];               // fetchs global variables; PHP allows only explicit expression of getting global variables
    $queryTableName = $GLOBALS["queryTableName"];

    $statement = $database -> prepare("SELECT query_count FROM " . $queryTableName. " WHERE team_id = ? AND network_id = ?");
    $statement -> bind_param("ii", $team, $network);
    $statement -> execute();
    $queryCount = NULL;
    $statement -> bind_result($queryCount);
    
    if(!$statement -> fetch()){         // inserts a record if no record found in the table
        $statement2 = $database -> prepare("INSERT INTO " . $queryTableName . " (team_id, network_id, query_count) VALUES (?, ?, 0)");
        $statement2 -> bind_param("ii", $team, $network);
        $statement2 -> execute();
        $statement2 -> close();
    }
    
    $statement -> close();
   
    return $queryCount;
    
}
$queryCountNetwork = $network;
if($fakeNetworkEnabled){
    $queryCountNetwork = $fakeNetwork;
}
$queryCount = getQueryCount($team, $queryCountNetwork);

$queryCondition = $queryCount < $maxQueryCount;
if($queryConditionTestEnabled){
    $queryCondition = true;   
}
if($queryCondition){
    $newQueryCount = $queryCount + 1;
    $statement = $database -> prepare("UPDATE " . $queryTableName . " SET query_count = ? WHERE team_id = ? AND network_id = ?");
    $statement -> bind_param("iii", $newQueryCount, $team, $queryCountNetwork);
    $statement -> execute();
    $statement -> close();
}
else{
    die("-1");
}
$queryCount ++;





// ==== Write the query results to standard output ====
function showTeamInformation($team, $queryCount){
    echo($team . "\n");
    echo($queryCount . "\n");
}
function showNodeInformation($network, $node, $primeKey, $nodeTypeCount, $newLine = true){
    $degree = getNodeDegree($network, $node);
    $nodeTypes = getNodeTypes($network, $node, $nodeTypeCount);
    if($GLOBALS["nodeEncodingEnabled"]){
        $node = convertNodeID($node, $primeKey);
    }
    echo($node . " " . $degree);
    for($i = 0; $i < $nodeTypeCount; $i ++){
            echo(" " . $nodeTypes[$i]);
    }
    if($newLine){
        echo("\n");
    }
}
function showEdgeInformation($network, $node1, $node2, $primeKey, $edgeTypeCount, $newLine = true){
    $edgeTypes = getEdgeTypes($network, $node1, $node2, $edgeTypeCount);
    if($GLOBALS["nodeEncodingEnabled"]){
        $node1 = convertNodeID($node1, $primeKey);
        $node2 = convertNodeID($node2, $primeKey);
    }
    echo($node1 . " " . $node2);
    for($i = 0; $i < $edgeTypeCount; $i ++){
        echo(" " . $edgeTypes[$i]);
    }
    if($newLine){
        echo("\n");
    }
}
function showNeighborInformation($network, $node, $neighbors, $primeKey, $nodeTypeCount, $edgeTypeCount){
    foreach($neighbors as $neighborNode){
        $edgeTypes = getEdgeTypes($network, $node, $neighborNode, $edgeTypeCount);
        showNodeInformation($network, $neighborNode, $primeKey, $nodeTypeCount, false);
        for($i = 0; $i < $edgeTypeCount; $i ++){
            echo(" " . $edgeTypes[$i]);
        }
        echo("\n");
    }
}
showTeamInformation($team, $queryCount);
showNodeInformation($network, $node, $primeKey, $nodeTypeCount);
showNeighborInformation($network, $node, $neighbors, $primeKey, $nodeTypeCount, $edgeTypeCount);

$database -> close();
?>
