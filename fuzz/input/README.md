# jq AFL++ seed corpus

This bundle contains AFL++-friendly seed directories for jq's main fuzzing
surfaces:

- `compile/`: raw jq filter programs for `jq_compile()`-style targets.
- `execute/`: delimiter-packed blobs for `tests/jq_fuzz_execute.cpp`.
- `fixed/`: delimiter-packed blobs plus selector bytes for `tests/jq_fuzz_fixed.cpp`.
- `parse/`: JSON and near-JSON seeds for `jv_parse()`-style targets.
- `parse_extended/`: 8-byte flag header plus payload for `jv_parse_custom_flags()`.
- `parse_stream/`: streaming-oriented JSON, multi-root, and malformed inputs.
- `load_file/`: JSON, text, sequences, and binary-ish files for `jv_load_file()`.
- `cli_filters/`: filter files for fuzzing the jq CLI with `-f @@`.
- `cli_json/`: JSON files for fuzzing the jq CLI with `@@` as the input file.
- `module_filters/` + `module_fixture/`: import/include seeds for CLI module loading.
- `dictionaries/`: optional AFL++ token dictionaries for jq and JSON.

Suggested AFL++ invocations:

```sh
afl-fuzz -i compile -o out-compile -- ./jq_fuzz_compile
afl-fuzz -i execute -o out-execute -- ./jq_fuzz_execute
afl-fuzz -i fixed -o out-fixed -- ./jq_fuzz_fixed
afl-fuzz -i parse -o out-parse -- ./jq_fuzz_parse
afl-fuzz -i parse_extended -o out-parse-ext -- ./jq_fuzz_parse_extended
afl-fuzz -i parse_stream -o out-parse-stream -- ./jq_fuzz_parse_stream
afl-fuzz -i load_file -o out-load -- ./jq_fuzz_load_file

# CLI campaigns
afl-fuzz -i cli_filters -o out-cli-filter -- ./jq -f @@ tests/torture/input0.json
afl-fuzz -i cli_json -o out-cli-json -- ./jq . @@
afl-fuzz -i module_filters -o out-cli-mod -- ./jq -L module_fixture -f @@ tests/torture/input0.json
```

Notes:

- `execute/` and `fixed/` are **not** plain text corpora. They are packed to
  match LLVM `FuzzedDataProvider::ConsumeRandomLengthString()` by using `\!`
  as a delimiter and doubling literal backslashes.
- `parse_extended/` files start with little-endian `uint32` values for jq parse
  flags and print flags, followed by the payload.
- `compile/` is intentionally mostly valid filters, with only a small set of
  invalid filters mixed in so the seed corpus stays useful for coverage-guided
  mutation.
