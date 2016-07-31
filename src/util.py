from datetime import datetime
import os

class LogMode:
    IGNORE = 0
    PRINT_ONLY = 1
    FILE_ONLY = 2
    PRINT_AND_FILE = 3
    MEMORY_ONLY = 4
    PRINT_AND_MEMORY = 5

    path = "log.txt"
    mode = PRINT_ONLY
    memory = []
    
    should_print = lambda: (LogMode.mode == LogMode.PRINT_ONLY
                         or LogMode.mode == LogMode.PRINT_AND_FILE
                         or LogMode.mdoe == LogMode.PRINT_AND_MEMORY)
    
    should_file = lambda: (LogMode.mode == LogMode.FILE_ONLY
                        or LogMode.mode == LogMode.PRINT_AND_FILE)
    
    should_memory = lambda: (LogMode.mode == LogMode.MEMORY_ONLY
                          or LogMode.mode == LogMode.PRINT_AND_MEMORY)

def set_log_path(log_path):
    LogMode.path = log_path

def set_log_mode(log_mode):
    LogMode.mode = log_mode

def log(s):
    if LogMode.should_print():
        print s
    if LogMode.should_file():
        ensure_file_path(LogMode.path)
        f = open(LogMode.path, 'a')
        f.write(s + os.linesep)
        f.close()
    if LogMode.should_memory():
        LogMode.memory.append(s)

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

def super_remove_dirs(*paths):
    if paths is not None:
        for path in paths:
            if os.path.exists(path):
                os.system('rm -r '+path)

def save_image(image, path):
    ensure_file_path(path)
    image.save(path)
            
def time_stamp():
    return str(datetime.now()).replace(':', ' ')
    
def ensure_file_path(path):
    head, tail = os.path.split(path)
    if not os.path.exists(head):
        os.makedirs(head)
        
