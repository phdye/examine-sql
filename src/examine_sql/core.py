import os
# import io
import shutil
import subprocess
# from glob import glob

from .clear import clear_console
from .names import FORMATTED_OUTPUT
from .context import ExamineContext, WhichLevel, FileContext, FileCurrent

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def process_files(args):

    # ctx.log = open(FILE_LOG, "w")
    # if not ctx.log:
    #     print("Error: Cannot open file/write log '%s'" % FILE_LOG)
    #     sys.exit(1)

    if args.format:
        if os.path.exists(args.debug):
            shutil.rmtree(args.debug, ignore_errors=True)

    if not os.path.exists(args.debug):
        os.makedirs(args.debug, exist_ok=True)

    ctx = ExamineContext(args)

    src = ctx.inputs

    if args.format:
        while src.idx < src.max:
            current = src.set_current(no_init=True)
            print("Processing file %d of %d : '%s'" %
                    (current.ordinal, src.max, src.files[src.idx]))
            do_format(current)
            src.idx += 1
        src.idx = 0
        src.set_current()

    while src.idx < src.max:

        current = src.current

        print("Processing file %d of %d : '%s'" %
                (current.ordinal, src.max, src.files[src.idx]))

        if ctx.args.display and os.path.exists(FORMATTED_OUTPUT):
            with open(FORMATTED_OUTPUT, "r") as f:
                print(f.read())

        if not os.path.exists(os.path.join(current.fmt_sql, "1")):
            if ctx.args.format:
                src.error("Source '{}' -- Mo EXEC SQL found"
                            .format(src.files[src.idx]))
                # src.next() inherent in error()
            else:
                print("*** No EXEC SQL segments found.")
                src.next()
            continue

        print("Processing EXEC SQL segments:  %d" % src.inner.max)

        examine_sql(src.inner)

        navigate(src, WhichLevel.INPUTS, "Next [next]/prior/error/quit ?")

    # ctx.log.close()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def examine_sql(ctx : FileContext):

    input_file = ctx.outer.current.file

    while ctx.idx < ctx.max:

        clear_console()
        segment = ctx.current.file
        print("Source: %s\n" % input_file)
        print("Sql: %d of %d\n" % (ctx.current.ordinal, ctx.max))
        print("Segment: '%s'\n" % segment)
        with open(segment, "r") as f:
            print(f.read())
        navigate(ctx, WhichLevel.SEGMENTS, "Next [next]/prior/error/quit ?")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def navigate(ctx, which, prompt):

    action = input(prompt+" [Next] ?  ").strip().lower() or "next"

    if action in ("err", "error", "save"):
        # shutil.copy(file, files.error_dir)
        ctx.next()
    elif action in ("p", "b", "prev", "prior", "back"):
        ctx.prior()
    elif action in ("q", "quit", "e", "exit"):
        exit(0)
    elif action in ("n", "next"):
        ctx.next()
    else:
        print("Unknown action: '%s'" % action)
        exit(1)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def do_format(ctx : FileCurrent) -> bool:

    try:
        os.remove(FORMATTED_OUTPUT)
    except OSError:
        pass

    input_file = ctx.file

    cmd = [ "python3", "-m", "proc_format", "--keep", 
                "--debug", os.path.dirname(ctx.fmt_sql),
                input_file, FORMATTED_OUTPUT]

    print("Running: %s" % " ".join(cmd))
    with open(ctx.log_file, "w") as log:
        proc = subprocess.Popen(
            cmd, env=dict(os.environ, PYTHONPATH=os.path.abspath("src")), stderr=log
        )
        proc.communicate()
        if proc.returncode != 0:
            print("Error during formatting. See log file for details: %s" % ctx.log_file)
            # TODO: log error to errors file
            # ctx.input.errors.append(input_file)
            return False

    return True
