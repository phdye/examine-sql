# `examine-sql` for `proc-format`

`examine-sql` is a command line tool specific to examining the debugging
output of `proc-format`, an Oracle Pro*C code formatter.

Examines proc-format's EXEC SQL pulled out of Pro*C (.pc) files in order
to format their C source code.

Fundamentally, one checks the extracted EXEC SQL to ensure that:
   - Only a single EXEC SQL statement is extracted per segment
   - No C code is has been inadvertently extracted

Checker needs to :
   - Recognize EXEC SQL statements start with 'EXEC ' and end with ';'
     - EXEC ORACLE statements are also supported
   - Be able to distinguish between SQL and C code

One does not need to:
    - Check the SQL for correctness or formatting
    - Need to understand the SQL or C code

Examines the debug output of `proc-format` residing in `debug/sql`

## Features

- Format SQL input files with the `--format` option -- runs `proc-format` on the specified input file(s).  Then shows each of the extracted `EXEC SQL ...` segments.
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
