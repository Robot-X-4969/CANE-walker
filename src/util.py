from datetime import datetime
import os

# The LogMode class stores log data for the module, which cleans up the 
# namespace of files that import this module
class LogMode:
    # Enumerate the log modes. Stdout will print log entries to the console.
    # Logfile will print to a file. Memory buffer will store a list of log 
    # entries, then (optionally) print all of them to a file at once.
    USE_STDOUT = 1
    USE_LOGFILE = 2
    USE_MEMORY_BUFFER = 3
    
    # Notes the defaults: console output only, ./log.txt if file logging
    # is specified with no file path
    path = "log.txt"
    modes = [USE_STDOUT]
    memory = []
    
    # Access the state of the logging modes
    @staticmethod
    def should_print():
        return LogMode.USE_STDOUT in LogMode.modes
    @staticmethod
    def should_file():
        return LogMode.USE_LOGFILE in LogMode.modes
    @staticmethod
    def should_memory():
        return LogMode.USE_MEMORY_BUFFER in LogMode.modes

# specify the directory/file in which logs will be stored if requested
def set_log_path(log_path):
    LogMode.path = log_path

# specify which modes (stdout, logfile, memory buffer) should be used.
# examples:
# 1.    util.set_log_modes(util.LogMode.USE_LOGFILE)
# 2.    util.set_log_modes(util.LogMode.USE_LOGFILE, util.LogMode.USE_STDOUT)
# 3.    util.set_log_modes()  *log data disappears into a black hole
def set_log_modes(*log_modes):
    LogMode.modes = log_modes

# call this method (util.log("hey, write this down")) to log string data
# in the previously specified mode and location
def log(string):
    if LogMode.should_print():
        print string
    if LogMode.should_file():
        ensure_file_path(LogMode.path)
        f = open(LogMode.path, 'a')
        f.write(string + os.linesep)
        f.close()
    if LogMode.should_memory():
        LogMode.memory.append(string)

# write strings from LogMode.memory to the previous specified file. If the
# "memory buffer" mode is inactive, LogMode.memory should be empty and this
# method should do nothing.
def save_log_memory_to_file():
    if (not LogMode.memory is None 
            and not LogMode.path is None 
            and len(LogMode.memory) > 0
    ):
        ensure_file_path(LogMode.path)
        f = open(LogMode.path, 'a')
        for line in LogMode.memory:
            f.write(line + os.linesep)
        f.close()
    LogMode.memory = []



# utility method: removes all specified directories and everything that is 
# inside them. Use with caution.
def super_remove_dirs(*paths):
    if paths is not None:
        for path in paths:
            if os.path.exists(path):
                os.system('rm -r '+path)

# Saves a PIL image, making sure it can do so first
def save_image(image, path):
    ensure_file_path(path)
    image.save(path)
    
# Finds the current date and time, then formats it so that it can be used
# in a file name
def time_stamp():
    return str(datetime.now()).replace(':', ' ')
    
# Check whether the directory in which a file will be located exists. If not,
# create it.
def ensure_file_path(path):
    head, tail = os.path.split(path)
    if not os.path.exists(head):
        os.makedirs(head)
        
