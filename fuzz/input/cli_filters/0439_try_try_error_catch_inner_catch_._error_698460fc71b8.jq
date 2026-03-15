try ((try error catch "inner catch \(.)")|error) catch "outer catch \(.)"
