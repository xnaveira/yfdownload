from clint.textui import puts, colored, indent
from enum import Enum, auto


class Level(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    SUCCESS = auto()


def output_print(msg,level=Level.INFO):
    if level == Level.INFO:
        print_function = colored.blue
    elif level == Level.WARNING:
        print_function = colored.yellow
    elif level == Level.ERROR:
        print_function = colored.red
    elif level == Level.SUCCESS:
        print_function = colored.green
    else:
        raise NameError

    with indent(4, quote='>>>'):
        puts(print_function(msg))