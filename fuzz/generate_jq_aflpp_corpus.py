#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import shutil
import struct
from collections import defaultdict
from pathlib import Path

RAW = Path('/mnt/data/jq_raw/tests')
OUT = Path('/mnt/data/jq_aflpp_corpus')

TEST_FILES = [
    RAW / 'jq.test',
    RAW / 'base64.test',
    RAW / 'man.test',
    RAW / 'manonig.test',
    RAW / 'onig.test',
    RAW / 'optional.test',
    RAW / 'uri.test',
]

PRINT_FLAGS = {
    'none': 0,
    'pretty': 1,
    'ascii': 2,
    'sorted': 8,
    'invalid': 16,
    'tab': 64,
    'space0': 256,
    'space1': 512,
    'space2': 1024,
    'pretty_ascii_sorted': 1 | 2 | 8,
}

PARSE_FLAGS = {
    'none': 0,
    'seq': 1,
    'streaming': 2,
    'stream_errors': 4,
    'seq_streaming': 1 | 2,
    'seq_stream_errors': 1 | 4,
    'streaming_errors': 2 | 4,
    'all': 1 | 2 | 4,
}

class SeedWriter:
    def __init__(self, root: Path):
        self.root = root
        self.counters: dict[Path, int] = defaultdict(int)
        self.seen: dict[Path, set[bytes]] = defaultdict(set)

    def write(self, rel_dir: str, label: str, data: bytes, suffix: str = '') -> Path | None:
        directory = self.root / rel_dir
        directory.mkdir(parents=True, exist_ok=True)
        if data in self.seen[directory]:
            return None
        self.seen[directory].add(data)
        self.counters[directory] += 1
        stem = sanitize(label)
        digest = hashlib.sha1(data).hexdigest()[:12]
        path = directory / f"{self.counters[directory]:04d}_{stem}_{digest}{suffix}"
        path.write_bytes(data)
        return path


def sanitize(label: str, max_len: int = 48) -> str:
    label = re.sub(r'[^A-Za-z0-9._-]+', '_', label.strip())
    label = re.sub(r'_+', '_', label).strip('._-')
    return (label or 'seed')[:max_len]


def parse_test_file(path: Path):
    valid_filters: list[str] = []
    invalid_filters: list[str] = []
    json_candidates: list[str] = []

    lines = path.read_text(encoding='utf-8').splitlines()
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if not stripped or line.lstrip().startswith('#'):
            i += 1
            continue

        if line.startswith('%%FAIL'):
            i += 1
            while i < n and (not lines[i].strip() or lines[i].lstrip().startswith('#')):
                i += 1
            if i < n:
                invalid_filters.append(lines[i])
                i += 1
            while i < n and lines[i].strip():
                i += 1
            continue

        program = line
        i += 1
        while i < n and (not lines[i].strip() or lines[i].lstrip().startswith('#')):
            i += 1
        if i >= n:
            break
        input_line = lines[i]
        i += 1
        outputs: list[str] = []
        while i < n and lines[i].strip():
            if not lines[i].lstrip().startswith('#'):
                outputs.append(lines[i])
            i += 1

        valid_filters.append(program)
        json_candidates.append(input_line)
        json_candidates.extend(outputs)

    return valid_filters, invalid_filters, json_candidates


def parse_c_string_array(path: Path, array_name: str) -> list[str]:
    text = path.read_text(encoding='utf-8')
    m = re.search(rf'{re.escape(array_name)}\s*\[\]\s*=\s*\{{(.*?)\n\}};', text, re.S)
    if not m:
        raise RuntimeError(f'Could not find {array_name} in {path}')
    body = m.group(1)
    tokens = re.finditer(r'"(?:\\.|[^"\\])*"|,', body, re.S)
    items: list[str] = []
    cur = ''
    for tok in tokens:
        s = tok.group(0)
        if s == ',':
            if cur:
                items.append(cur)
                cur = ''
        else:
            cur += ast.literal_eval(s)
    if cur:
        items.append(cur)
    return items


def is_json_value(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except Exception:
        return False


def dedupe_keep_order(items):
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def fdp_escape(data: bytes) -> bytes:
    return data.replace(b'\\', b'\\\\')


def fdp_pack_strings(*segments: bytes) -> bytes:
    # FuzzedDataProvider::ConsumeRandomLengthString treats backslash followed by a
    # non-backslash as a terminator. Use b"\\!" as the delimiter and escape all
    # literal backslashes.
    delim = b'\\!'
    return delim.join(fdp_escape(s) for s in segments) + delim


def build_synthetic_json_seeds() -> list[tuple[str, bytes]]:
    seeds: list[tuple[str, bytes]] = []

    def add(name: str, payload: bytes):
        seeds.append((name, payload))

    add('null', b'null')
    add('true', b'true')
    add('false', b'false')
    add('zero', b'0')
    add('minus_one', b'-1')
    add('big_int', b'12345678909876543212345')
    add('tiny_float', b'1e-308')
    add('huge_float', b'1e308')
    add('empty_string', b'""')
    add('escapes', b'"Aa\\r\\n\\t\\b\\f\\u03bc"')
    add('bom_string', b'\xef\xbb\xbf"byte order mark"')
    add('empty_array', b'[]')
    add('empty_object', b'{}')
    add('single_elem_array', b'[0]')
    add('flat_array', b'[1,2,3,4,5]')
    add('mixed_array', b'[1,null,true,false,"abcdef",{},[],[1,2,3]]')
    add('nested_array', b'[1,[2,[[3]]],{"a":[1,[2]]}]')
    add('simple_object', b'{"a":1}')
    add('compound_object', b'{"foo":{"bar":42},"bar":"badvalue","arr":[1,2,3],"nul":null}')
    add('unicode_object', b'{"mu":"\\u03bc","emoji":"\\ud83d\\ude03"}')
    add('dup_keys', b'{"a":1,"a":2,"b":3}')
    add('whitespace', b' \n\t {\n  "a" : [ 1 , 2 , 3 ] , "b" : { "c" : true }\n } \n')
    add('multi_roots_space', b'0 1 2')
    add('multi_roots_newline', b'{"a":1}\n{"b":2}\n[3,4]\n')
    add('stream_like', b'[[0],[]]\n[[1],"a"]\n[[2,0],"b"]\n')
    add('json_seq', b'\x1e{"a":1}\n\x1e[1,2]\n\x1enull\n')
    add('plain_text', b'not json at all\njust text\n')
    add('nul_bytes', b'{"a":"abc"}\x00\x00tail')
    add('invalid_utf8', b'\xff\xfe\xfd')
    add('incomplete_object', b'{')
    add('incomplete_array', b'[1,2')
    add('bad_object_syntax', b'{"a":}')
    add('bad_number_leading_zero', b'01')
    add('bad_string_escape', b'"\\v"')

    deep_array = ('[' * 128 + '0' + ']' * 128).encode('ascii')
    deep_object = ('{"a":' * 64 + '0' + '}' * 64).encode('ascii')
    add('deep_array_128', deep_array)
    add('deep_object_64', deep_object)
    return seeds


def build_module_fixture(dst: Path) -> None:
    fixture = dst / 'module_fixture'
    if fixture.exists():
        shutil.rmtree(fixture)
    fixture.mkdir(parents=True)
    # Copy the real jq module fixtures we downloaded.
    src_modules = RAW / 'modules'
    for item in src_modules.iterdir():
        if item.is_file():
            shutil.copy2(item, fixture / item.name)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    writer = SeedWriter(OUT)

    valid_filters: list[str] = []
    invalid_filters: list[str] = []
    json_candidates: list[str] = []

    for test_file in TEST_FILES:
        vf, inf, jc = parse_test_file(test_file)
        valid_filters.extend(vf)
        invalid_filters.extend(inf)
        json_candidates.extend(jc)

    # Add plain jq files from tests that are top-level filters (not module defs).
    top_level_filter_files = [
        RAW / 'no-main-program.jq',
        RAW / 'yes-main-program.jq',
    ]
    valid_filters.extend(p.read_text(encoding='utf-8').strip() for p in top_level_filter_files)

    # Extract the built-in filter corpus from the fixed harness.
    fixed_programs = parse_c_string_array(RAW / 'jq_fuzz_fixed.cpp', 'jq_progs')
    valid_filters.extend(fixed_programs)

    # Hand-authored filters that are good AFL++ seeds and/or module-loading probes.
    extra_filters = [
        '.',
        '.[]',
        '.foo?',
        '. as $x | $x',
        'try .a catch .',
        'reduce .[] as $x (0; . + $x)',
        'foreach .[] as $x (0; . + $x; .)',
        'path(..)',
        'tostream',
        'fromstream(inputs)',
        'import "a" as a; a::a',
        'include "shadow1"; e',
        'import "test_bind_order" as t; t::check',
    ]
    valid_filters.extend(extra_filters)

    valid_filters = [f.strip() for f in valid_filters if f.strip()]
    invalid_filters = [f.strip() for f in invalid_filters if f.strip()]

    # Separate import/include filters; they need a module fixture for CLI use and
    # are not suitable for the bare compile/execute harnesses.
    module_filters = dedupe_keep_order([
        f for f in valid_filters if re.search(r'\b(?:import|include)\b', f)
    ])
    bare_filters = dedupe_keep_order([
        f for f in valid_filters if not re.search(r'\b(?:import|include)\b', f)
    ])
    invalid_filters = dedupe_keep_order(invalid_filters)

    valid_json_texts = dedupe_keep_order([t for t in json_candidates if is_json_value(t)])
    # Bring in jq's own standalone data files.
    valid_json_texts.append((RAW / 'torture' / 'input0.json').read_text(encoding='utf-8').strip())
    valid_json_texts.append((RAW / 'modules' / 'data.json').read_text(encoding='utf-8').strip())
    valid_json_texts = dedupe_keep_order([t for t in valid_json_texts if t.strip()])

    synthetic_json = build_synthetic_json_seeds()

    # Write compile/CLI filters.
    for filt in bare_filters:
        writer.write('compile', filt[:48], (filt + '\n').encode('utf-8'), '.jq')
        writer.write('cli_filters', filt[:48], (filt + '\n').encode('utf-8'), '.jq')

    # Add a modest number of invalid filters to the compile corpus to hit parser
    # error-handling without swamping the valid seeds.
    for filt in invalid_filters[:32]:
        writer.write('compile', 'invalid_' + filt[:40], (filt + '\n').encode('utf-8'), '.jq')

    # Module-specific CLI filters.
    module_seed_programs = module_filters + [
        'import "a" as a; a::a',
        'include "shadow1"; e',
        'import "test_bind_order" as t; t::check',
    ]
    for filt in dedupe_keep_order([f.strip() for f in module_seed_programs if f.strip()]):
        writer.write('module_filters', filt[:48], (filt + '\n').encode('utf-8'), '.jq')

    # JSON-oriented corpora.
    valid_json_bytes = [(f'extracted_{i:03d}', txt.encode('utf-8')) for i, txt in enumerate(valid_json_texts, 1)]
    for label, data in valid_json_bytes:
        writer.write('parse', label, data, '.json')
        writer.write('cli_json', label, data, '.json')
        writer.write('parse_stream', label, data, '.json')
        writer.write('load_file', label, data, '.bin')

    for label, data in synthetic_json:
        # Keep parse/cli_json mostly valid; only place invalid/plain-text seeds in
        # parse/load_file/parse_stream.
        if label not in {
            'plain_text', 'nul_bytes', 'invalid_utf8', 'incomplete_object', 'incomplete_array',
            'bad_object_syntax', 'bad_number_leading_zero', 'bad_string_escape', 'stream_like', 'json_seq',
            'multi_roots_space', 'multi_roots_newline'
        }:
            writer.write('parse', label, data, '.json')
            writer.write('cli_json', label, data, '.json')
        else:
            writer.write('parse', label, data, '.bin')
        writer.write('parse_stream', label, data, '.bin' if b'\x1e' in data or b'\x00' in data or not data.startswith((b'{', b'[', b'"', b't', b'f', b'n', b'-', b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b' ')) else '.json')
        writer.write('load_file', label, data, '.bin')

    # Structured execute corpus: exact segments for FuzzedDataProvider.
    execute_filters = bare_filters[:128]
    valid_json_pool = [data for _, data in valid_json_bytes] + [data for name, data in synthetic_json if name not in {
        'plain_text', 'nul_bytes', 'invalid_utf8', 'incomplete_object', 'incomplete_array',
        'bad_object_syntax', 'bad_number_leading_zero', 'bad_string_escape', 'json_seq'
    }]
    valid_json_pool = dedupe_keep_order(valid_json_pool)
    if not valid_json_pool:
        raise RuntimeError('No valid JSON seeds collected')

    for idx, filt in enumerate(execute_filters):
        j1 = valid_json_pool[idx % len(valid_json_pool)]
        j2 = valid_json_pool[(idx * 7 + 3) % len(valid_json_pool)]
        blob = fdp_pack_strings(filt.encode('utf-8'), j1, j2)
        writer.write('execute', filt[:40], blob, '.bin')

    # Structured fixed-harness corpus: two FDP strings, then selector bytes.
    fixed_count = len(fixed_programs)
    selector_size = 1 if fixed_count <= 256 else 2
    for idx in range(fixed_count):
        j1 = valid_json_pool[idx % len(valid_json_pool)]
        j2 = valid_json_pool[(idx * 11 + 5) % len(valid_json_pool)]
        blob = bytearray(fdp_pack_strings(j1, j2))
        if selector_size == 1:
            blob += bytes([idx & 0xFF])
        else:
            blob += bytes([idx & 0xFF, (idx >> 8) & 0xFF])
        writer.write('fixed', f'selector_{idx:03d}', bytes(blob), '.bin')

    # Parse-extended seeds: 4-byte fuzz flags + 4-byte dump flags + payload.
    pe_payloads = [
        ('empty_string', b'""'),
        ('simple_object', b'{"a":1}'),
        ('nested_array', b'[1,[2,[[3]]]]'),
        ('multi_roots', b'{"a":1}\n{"b":2}\n'),
        ('json_seq', b'\x1e{"a":1}\n\x1e[1,2]\n'),
        ('bad_object', b'{"a":}'),
    ]
    for pf_name, pf in PARSE_FLAGS.items():
        for df_name, df in PRINT_FLAGS.items():
            for label, payload in pe_payloads[:3 if pf_name == 'none' and df_name == 'none' else 1]:
                blob = struct.pack('<I', pf) + struct.pack('<I', df) + payload
                writer.write('parse_extended', f'{pf_name}_{df_name}_{label}', blob, '.bin')
    # Add a few explicitly interesting mixed cases.
    for pf_name, df_name, label, payload in [
        ('streaming', 'none', 'multi_roots', b'{"a":1}\n{"b":2}\n'),
        ('streaming_errors', 'invalid', 'bad_object', b'{"a":}'),
        ('seq', 'pretty', 'json_seq', b'\x1e{"a":1}\n\x1e[1,2]\n'),
        ('all', 'pretty_ascii_sorted', 'empty_string', b'""'),
    ]:
        blob = struct.pack('<I', PARSE_FLAGS[pf_name]) + struct.pack('<I', PRINT_FLAGS[df_name]) + payload
        writer.write('parse_extended', f'{pf_name}_{df_name}_{label}', blob, '.bin')

    build_module_fixture(OUT)

    # Dictionaries are optional but useful with AFL++.
    (OUT / 'dictionaries').mkdir(exist_ok=True)
    (OUT / 'dictionaries' / 'json.dict').write_text(
        '\n'.join([
            '"{"', '"}"', '"["', '"]"', '":"', '","', '"true"', '"false"', '"null"',
            '"\\\\u"', '"\\\\n"', '"\\\\r"', '"\\\\t"', '"\""'
        ]) + '\n',
        encoding='utf-8'
    )
    (OUT / 'dictionaries' / 'jq.dict').write_text(
        '\n'.join([
            '"."', '".[]"', '".foo"', '"|"', '","', '"[]"', '"{}"', '"select"', '"map"',
            '"reduce"', '"foreach"', '"as"', '"def"', '"if"', '"then"', '"else"', '"end"',
            '"try"', '"catch"', '"?"', '"//"', '"|="', '"+="', '"-="', '"*="', '"/="',
            '"import"', '"include"', '"tostream"', '"fromstream"', '"recurse"', '"walk"',
            '"match"', '"gsub"', '"sub"', '"capture"'
        ]) + '\n',
        encoding='utf-8'
    )

    readme = f'''# jq AFL++ seed corpus

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
  match LLVM `FuzzedDataProvider::ConsumeRandomLengthString()` by using `\\!`
  as a delimiter and doubling literal backslashes.
- `parse_extended/` files start with little-endian `uint32` values for jq parse
  flags and print flags, followed by the payload.
- `compile/` is intentionally mostly valid filters, with only a small set of
  invalid filters mixed in so the seed corpus stays useful for coverage-guided
  mutation.
'''
    (OUT / 'README.md').write_text(readme, encoding='utf-8')

    # Tar/zip deliverables.
    shutil.make_archive('/mnt/data/jq_aflpp_corpus', 'zip', OUT)

    counts = {}
    for path in sorted(OUT.iterdir()):
        if path.is_dir():
            counts[path.name] = sum(1 for p in path.rglob('*') if p.is_file())
    summary_lines = [f'{k}: {v}' for k, v in sorted(counts.items())]
    (OUT / 'COUNTS.txt').write_text('\n'.join(summary_lines) + '\n', encoding='utf-8')

if __name__ == '__main__':
    main()
