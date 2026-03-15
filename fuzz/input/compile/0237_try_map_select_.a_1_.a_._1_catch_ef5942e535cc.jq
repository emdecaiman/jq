try ((map(select(.a == 1))[].a) |= .+1) catch .
