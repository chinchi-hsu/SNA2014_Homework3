<?php
include("database_info.php");
$database = new mysqli($databaseURL, $databaseAccount, $databasePassword, $databaseName);
$network = 1;

// ==== Select one node from the graph uniformly at random ====
$statement = $database -> prepare("SELECT node FROM " . $nodeTableName . " WHERE network_id = ? ORDER BY RAND() LIMIT 1");
$statement -> bind_param("i", $network);
$statement -> execute();
$node = NULL;           // the randomly selected node is stored in $node
$statement -> bind_result($node);
$statement -> fetch();
$statement -> close();





// ==== Run a random expansion starting from the sampled node ====
function getNodeNeighborSet($network, $node){
    $database = $GLOBALS["database"];
    $nodeTableName = $GLOBALS["nodeTableName"];

    $statement = $database -> prepare("SELECT neighbors FROM " . $nodeTableName . " WHERE network_id = ? AND node = ?");
    $statement -> bind_param("ii", $network, $node);
    $statement -> execute();
    $neighborWord = NULL;
    $statement -> bind_result($neighborWord);
    $statement -> fetch();
    $statement -> close();
    
    $neighborSet = array();
    $neighborStrs = explode(",", $neighborWord);
    foreach($neighborStrs as $neighborStr){
        $neighborSet[$neighborStr] = 0;
    }

    return $neighborSet;
}
function addToEdgeSet(&$edgeSet, $node1, $node2){
    $nodeFrom = min($node1, $node2);
    $nodeTo = max($node1, $node2);
    if(!array_key_exists($nodeFrom, $edgeSet)){
        $edgeSet[$nodeFrom] = array();
    }
    $edgeSet[$nodeFrom][$nodeTo] = 0; 
}
function getIntersection($set1, $set2){
    $intersection = array();
    $minSet = (count($set1) < count($set2)) ? $set1 : $set2;
    $maxSet = (count($set1) < count($set2)) ? $set2 : $set1;
    foreach($minSet as $element => $value){
        if(array_key_exists($element, $maxSet)){
            $intersection[$element] = 0;
        }
    }
    return $intersection;
}

$seedNodeCount = 100;
$seedNodeSet = array($node => 0);
$seedEdgeSet = array();
while(count($seedNodeSet) < $seedNodeCount){
    $node = array_rand($seedNodeSet);   // Randomly sample a known node
    
    $neighborSet = getNodeNeighborSet($network, $node);
    $neighbor = array_rand($neighborSet);
    if(array_key_exists($neighbor, $seedNodeSet)){
        continue;
    }
    
    $edgeSideSet = getIntersection(getNodeNeighborSet($network, $neighbor), $seedNodeSet);
    foreach($edgeSideSet as $edgeSideNode => $value){
        addToEdgeSet($seedEdgeSet, $neighbor, $edgeSideNode);
    }
    $seedNodeSet[$neighbor] = 0;
}





// ==== Write the random sampled graph into the data ====
$outFile = fopen("seed.txt", "w");
foreach($seedEdgeSet as $nodeFrom => $nodeToSet){
    foreach($nodeToSet as $nodeTo => $value){
        fprintf($outFile, "%d\t%d\n", $nodeFrom, $nodeTo);
    } 
}
fclose($outFile);


?>
