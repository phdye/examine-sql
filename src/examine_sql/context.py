import argparse
import os
import io
import sys
import shutil
import subprocess
from glob import glob

from .enum import Enum
from .names import FORMAT_DIR, EXAMINE_DIR, SQL_DIR, ERRORS_FILE, LOG_FILE

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class WhichLevel(Enum):
    INPUTS = 1
    SEGMENTS = 2
    def alter(self):
        return WhichLevel.INPUTS if self == WhichLevel.SEGMENTS else WhichLevel.SEGMENTS
    def __str__(self):
        return "Inputs" if self == WhichLevel.INPUTS else "Segments"

class WhichTwin(Enum):
    FORMAT = 1
    EXAMINE = 2
    def twin(self):
        return WhichTwin.FORMAT if self == WhichTwin.EXAMINE else WhichTwin.EXAMINE
    def __str__(self):
        return FORMAT_DIR if self == WhichTwin.FORMAT else EXAMINE_DIR

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class FileContext:
    __slots__ = ["level", "prompt", "files", "base_dir", "log_file", "idx", "max", "errors",
                "current", "outer", "inner", "init"]
    def __init__(self, level, prompt, files, base_dir, outer=None, init=None):
        self.level = level
        self.prompt = prompt
        self.files = files
        # 1. 'debug/' 2. 'debug/<file-idx>/format/' 3. 'debug/<file-idx>/examine/'
        self.base_dir = base_dir # 
        # 1. Inputs:   'debug/' 
        # 4/5 Format:   'debug/<file-idx>/format/'
        # 4/6 Examine:  'debug/<file-idx>/examine/'
        self.idx = 0
        self.max = len(files)
        self.errors = []
        self.outer = outer # outer context, if any
        self.init = init # step intializer, if any
        # shutil.rmtree(self.base_dir, ignore_errors=True)
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir, exist_ok=True)
        self.set_current()
        self.inner = None
    def name(self):
        return str(self.level)
    def alter(self):
        return self.level.alter()
    def next(self):
        self.idx += 1
        # print("%s : next() : idx: %d, max: %d" % 
        #         ( str(self.level), self.idx, self.max))
        if self.idx < self.max:
            self.set_current()
            # print("idx: %d, max: %d" % (self.idx, self.max))
            return
        # if self.outer:
        #     print("Outer:  idx: %d, max: %d" % (self.outer.idx, self.outer.max))
        #     print("Inner:  idx: %d, max: %d" % (self.outer.inner.idx, self.outer.inner.max))
    def prior(self):
        self.idx -= 1
        if self.idx >= 0:
            self.set_current()
            return
        if self.outer:
            self.outer.prior()
            return
        print("*** Beginning of file list (no prior file).")
    def error(self, message):
        # Show record error only once, despite back navigation
        print("*** Error: %s" % message)
        # list is empty or different error message
        if not self.errors or self.errors[-1] != message:
            self.errors.append(message)
            append_file(self.current.errors_file, None, content=message)
        self.next()
    def set_current(self, no_init=False):
        self.current = FileCurrent(ctx=self)
        if not no_init and self.init and not self.init(self):
            return None
        return self.current

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class FileCurrent:
    __slots__ = ["idx", "ordinal", "file", "ord_dir", "base_dir", "sql_dir", "fmt_sql",
                "log_file", "errors_file"]
    def __init__(self, ctx : FileContext):
        self.idx = ctx.idx
        self.ordinal = self.idx + 1
        self.file = ctx.files[self.idx]
    
        # 4 Format:   'debug/<file-ord>'
        self.ord_dir = format_name(ctx.base_dir, "{}".format(self.ordinal))
    
        # 5 Examine:  'debug/<file-ord>/examine/'
        self.base_dir = format_name(self.ord_dir, EXAMINE_DIR)
   
        # 9 Examine:  'debug/<file-ord>/examine/sql'
        self.sql_dir = format_name(self.base_dir, SQL_DIR)
        if not os.path.exists(self.sql_dir):
            os.makedirs(self.sql_dir, exist_ok=True)

        # . Format:   'debug/<file-ord>/format/sql'
        self.fmt_sql = format_name(self.ord_dir, FORMAT_DIR, SQL_DIR)
    
        # 7 Examine:  'debug/<file-ord>/examine/log.txt'
        self.log_file = format_name(self.base_dir, LOG_FILE)
        touch(self.log_file)

        # 8 Examine:  'debug/<file-ord>/examine/errors.txt'
        self.errors_file = format_name(self.base_dir, ERRORS_FILE)
        touch(self.errors_file)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class ExamineContext:
    __slots__ = ["args", "inputs", "log"]
    def __init__(self, args):
        self.args = args
        prompt = "Next [next]/prior/error/quit ?"
        self.inputs = FileContext( WhichLevel.INPUTS, prompt, args.input_files,
                        args.debug, init=segments_init)
        self.log = None # thus far

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def segments_init(ctx : FileContext):
    print("- sements_init")
    def segment_key(segment_file):
        return int(os.path.basename(segment_file))
    current = ctx.current
    expr = format_name(current.fmt_sql, "[0-9]*")    
    print("expr: %s" % expr)
    segments = sorted(glob(expr), key=segment_key)
    print("segments: %s" % segments)
    if len(segments) == 0:
        print("*** No extracted EXEC SQL segments found.")
        return False
    prompt = "EXEC SQL segment [next]/prior/error/quit ?"
    ctx.inner = FileContext(WhichLevel.SEGMENTS, prompt, segments,
                                current.base_dir, outer=ctx)
    return True

def format_name(debug_dir, *elements):
    if elements[0] is None:
        elements = []
    elements = [str(e) for e in elements]
    return os.path.join(debug_dir, *elements)

def open_file(debug_dir, *elements, mode='w'):
    return open(format_name(debug_dir, *elements), mode)

def write_file(debug_dir, file_name, content):
    with open_file(debug_dir, file_name) as f:
        f.write(content)

def append_file(debug_dir, file_name, content):
    with open_file(debug_dir, file_name, 'a') as f:
        f.write(content)

def touch(file_name, times=None):
    with open(file_name, 'a'):
        os.utime(file_name, times)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
