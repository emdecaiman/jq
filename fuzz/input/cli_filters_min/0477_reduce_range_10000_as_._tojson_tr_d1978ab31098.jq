reduce range(10000) as $_ ([];[.]) | tojson | try (fromjson) catch . | (contains("<skipped: too deep>") | not) and contains("Exceeds depth limit for parsing")
