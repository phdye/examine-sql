# Examine SQL for `proc-format`

Examine SQL is a command-line tool to process and examine SQL files with various formatting and display options.

Examines the debug output of `proc-format` residing in `debug/sql`

## Features

- Format SQL input files with the `--format` option -- runs `proc-format` on the specified files.  Then shows each of the extracted `EXEC SQL ...` segments.
- Display formatted output with the `--display` option.  Displays the formated Pro*C code -- only the C code is formatted.
- Navigate and handle SQL segments interactively.

## Installation

```bash
pip install examine-sql
```

## Usage

```bash
examine-sql [-f | --format] [-d | --display] [<input_file> ...]
```

### Examples

Format and display an input file:
```bash
examine-sql -f -d examples/basic/unformatted.pc
```

## License

MIT License
