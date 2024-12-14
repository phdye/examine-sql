import argparse
import os
import subprocess
from pathlib import Path

VERSION = "1.0.0"

USAGE = """Usage:
    examine-sql.py [-f | --format] [-d | --display] [<input_file> ...]

Options:
    -f --format    Format the SQL input.
    -d --display   Display the output after processing.
    -h --help      Show this help message.
    --version      Show the version number.

Examples:
    examine-sql.py -f -d examples/basic/unformatted.pc
"""

def process_files(input_files, format_flag, display_flag):
    log_file = Path("errors.txt")
    formatted_output = Path("debug/formated.pc")
    sql_dir = Path("debug/sql")
    counter = 0

    for input_file in input_files:
        if format_flag:
            formatted_output.unlink(missing_ok=True)
            cmd = [
                "python", "-m", "proc_format", input_file, str(formatted_output)
            ]
            print(f"Running: {' '.join(cmd)}")
            with open(log_file, "w") as log:
                result = subprocess.run(cmd, env={"PYTHONPATH": str(Path("src").resolve())}, text=True, stderr=log)
            if result.returncode != 0:
                print("Error during formatting. See log file for details.")
                return

        if display_flag and formatted_output.exists():
            print(formatted_output.read_text())

        if not (sql_dir / "1").exists():
            print("*** No EXEC SQL extracted!")
        else:
            errors_dir = Path("debug/errors")
            errors_dir.mkdir(parents=True, exist_ok=True)

            sql_files = sorted(f for f in sql_dir.iterdir() if f.name.isdigit())
            if not sql_files:
                print("*** No SQL segments found!")
                continue

            for idx, segment in enumerate(sql_files, 1):
                print(f"Sql: {idx} of {len(sql_files)}")
                print(f"Segment: '{segment}'")
                print(segment.read_text())
                action = input("Action [Next]? ").strip().lower() or "next"
                if action in {"err", "error", "save"}:
                    (errors_dir / segment.name).write_text(segment.read_text())
                elif action in {"p", "b", "prev", "prior", "back"}:
                    continue
                elif action in {"q", "quit", "e", "exit"}:
                    exit(0)

        counter += 1
        if counter < len(input_files):
            input("Next source file? ")

def main():
    parser = argparse.ArgumentParser(
        description="Examine and process SQL files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=USAGE,
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
        "--version", action="version", version=f"%(prog)s {VERSION}"
    )

    args = parser.parse_args()
    process_files(args.input_files, args.format, args.display)

if __name__ == "__main__":
    main()
