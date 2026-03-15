(add / length) as $m | map((. - $m) as $d | $d * $d) | add / length | sqrt
