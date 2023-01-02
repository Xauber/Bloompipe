import os
def get_current_directory():
    return os.path.dirname(os.path.abspath("__file__"))
def get_parent_directory():
    return get_parent_directory_for(get_current_directory())
def get_parent_directory_for(directory):
    return os.path.abspath(os.path.join(directory, os.pardir))
def get_home_path():
    return os.path.expanduser("~")
