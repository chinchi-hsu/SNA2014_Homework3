<?php

function extendedEuclidean($a, $b){
    if($b == 0){
        return array(1, 0);
    }
    $pair = extendedEuclidean($b, $a % $b);

    return array($pair[1], $pair[0] - (int)($a / $b) * $pair[1]);
}

// Source: xy = 1 (mod p) where p is a prime
// yx + qp = gcd(x, p) = 1, 0 <= y < p, 0 <= x < p
function convertNodeID($x, $p){
    $pair = extendedEuclidean($x, $p);
    $y = $pair[0];
    for(; $y < 0; $y += $p);
    for(; $y >= $p; $y -= $p);
    return $y;
}

?>
