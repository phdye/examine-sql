import argparse
import sys

# from .enum import Enum
# from .clear import clear_console

from .context import ExamineContext
from .core import process_files
from .names import DEFAULT_DEBUG

VERSION = "0.3.0"

USAGE = """
Examine proc-format's the EXEC SQL pulled out of Pro*C (.pc)
files in order to format their C source code.  Fundamentally,
one checks the EXEC SQL to ensure that:
   - Only SQL a single EXEC SQL statement is extracted per segment
   - No C code is has been inadvertently extracted

Checker needs to :
   - Recognize EXEC SQL statements start with 'EXEC ' and end with ';'
     - EXEC ORACLE statements are also supported
   - Be able to distinguish between SQL and C code

One does not need to:
    - Check the EXEC SQL for correctness or formatting
    - Understand the EXEC SQL or C code

Usage:
    examine-sql [options] [<input_file> ...]

If <input_file> is not provided, the default is 'examples/basic/unformatted.pc'.

If <input_file> is '-', read Pro*C file names from standard input.

Options:
    -e, --examine=FILE  File listing .pc files to examine.
    -f --format         Format the SQL input.
    -d --display        Display the output after processing.
    -h --help           Show this help message.
    --version           Show the version number.

Examples:
    examine-sql.py -f -d examples/basic/unformatted.pc
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def main():
    parser = argparse.ArgumentParser(
        description="Process Pro*C file(s) and examine the captured EXE SQL segments.",
        epilog=USAGE,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-e", "--examine", help="File listing .pc files to examine."
    )
    parser.add_argument(
        "-f", "--format", action="store_true", help="Format the SQL input."
    )
    parser.add_argument(
        "-d", "--display", action="store_true", help="Display the output after processing."
    )
    parser.add_argument(
        "input_files", nargs="*", default=["examples/basic/unformatted.pc"], help="Input files to process."
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + VERSION
    )
    parser.add_argument("--debug", default=DEFAULT_DEBUG, help="Path to base debug directory.")

    args = parser.parse_args()

    if args.examine:
        with open(args.examine, "r") as f:
            more_files = [line.strip() for line in f.readlines()]
            more_files.extend(args.input_files)
            args.input_files = more_files

    process_files(args)

if __name__ == "__main__":
    main()

