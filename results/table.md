| Dataset | Bytes in | HUF bytes | gzip bytes | HUF encode ms | gzip encode ms |
|---|---:|---:|---:|---:|---:|
| empty | 0 | 26 | 20 | 0.005 | 0.036 |
| tiny_text | 13 | 54 | 33 | 0.025 | 0.037 |
| single_symbol | 65536 | 8220 | 97 | 9.766 | 0.23 |
| repeated_text | 65536 | 35754 | 351 | 11.912 | 0.388 |
| skewed_symbols | 65536 | 15373 | 19155 | 11.317 | 71.296 |
| uniform_bytes | 65536 | 66074 | 597 | 10.971 | 0.274 |
| random_bytes | 65536 | 66074 | 65574 | 11.191 | 1.131 |
| source_code | 8435 | 5172 | 2889 | 1.473 | 0.196 |
