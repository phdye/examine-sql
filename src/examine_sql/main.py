import argparse
import os
import shutil
import subprocess
from glob import glob

from .clear import clear_console

VERSION = "1.0.0"

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

Options:
    -f --format    Format the SQL input.
    -d --display   Display the output after processing.
    -h --help      Show this help message.
    --version      Show the version number.

Examples:
    examine-sql.py -f -d examples/basic/unformatted.pc
"""

def main():
    parser = argparse.ArgumentParser(
        description="Examine and process SQL files.",
        epilog=USAGE,
        formatter_class=argparse.RawDescriptionHelpFormatter,
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

    args = parser.parse_args()
    process_files(args.input_files, args.format, args.display)

def process_files(input_files, format_flag, display_flag):
    log_file = "errors.txt"
    formatted_output = "debug/formated.pc"
    sql_dir = "debug/sql"
    counter = 0

    for input_file in input_files:
        if format_flag:
            try:
                os.remove(formatted_output)
            except OSError:
                pass

            cmd = [
                "python", "-m", "proc_format", input_file, formatted_output
            ]
            print("Running: %s" % " ".join(cmd))
            with open(log_file, "w") as log:
                proc = subprocess.Popen(
                    cmd, env=dict(os.environ, PYTHONPATH=os.path.abspath("src")), stderr=log
                )
                proc.communicate()
                if proc.returncode != 0:
                    print("Error during formatting. See log file for details.")
                    return

        if display_flag and os.path.exists(formatted_output):
            with open(formatted_output, "r") as f:
                print(f.read())

        if not os.path.exists(os.path.join(sql_dir, "1")):
            print("*** No EXEC SQL extracted!")
        else:
            errors_dir = "debug/errors"
            if not os.path.exists(errors_dir):
                os.makedirs(errors_dir)

            sql_files = sorted(glob(os.path.join(sql_dir, "[0-9]*")))
            if not sql_files:
                print("*** No SQL segments found!")
                continue

            for idx, segment in enumerate(sql_files, 1):
                clear_console()
                print("Sql: %d of %d" % (idx, len(sql_files)))
                print("Segment: '%s'\n" % segment)
                with open(segment, "r") as f:
                    print(f.read())
                action = input("Action [Next]? ").strip().lower() or "next"
                if action in ("err", "error", "save"):
                    shutil.copy(segment, errors_dir)
                elif action in ("p", "b", "prev", "prior", "back"):
                    continue
                elif action in ("q", "quit", "e", "exit"):
                    exit(0)

        counter += 1
        if counter < len(input_files):
            input("Next source file? ")

if __name__ == "__main__":
    main()
