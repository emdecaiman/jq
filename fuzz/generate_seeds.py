import itertools, json, os

filters = [
".",
"map(.)",
"map(.+1)",
"select(.>1)",
"length",
"keys",
"values",
"..",
"paths",
"flatten",
"sort",
"unique",
"group_by(.)"
]

inputs = [
[1,2,3],
{"a":1,"b":2},
{"a":[1,2]},
[[1],[2]],
{"a":{"b":1}},
"hello",
123,
True
]

dirname = "seed"

os.makedirs(dirname, exist_ok=True)

i=0
for f,j in itertools.product(filters,inputs):
    open(f"{dirname}/seed{i:03d}","w").write(f+json.dumps(j))
    i+=1