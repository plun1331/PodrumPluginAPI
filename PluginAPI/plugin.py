# External Modules
import inspect
from podrum.command.CommandManager import CommandManager
import traceback
import sys
import inspect
from PluginAPI.errors import CommandInvokeError, MissingRequiredArgument, TooManyArguments



class Commands:
    def __init__(self):
        self.name = None
        self.description = None
        self.usage = None
        self.func = None
        self.plugin = None
    
    def execute(self, sender, args):
        arg = [sender]
        arg.extend(args[1:])
        args = arg
        argcopy = args
        self.plugin.events['before_command_invoke'](self, sender, args)
        argspec = inspect.getfullargspec(self.func)
        kwargs = None
        if not inspect.ismethod(self.func):
            pos_args = len(argspec[0])-1 if argspec[0] is not None else 0
        else:
            pos_args = len(argspec[0])-2 if argspec[0] is not None else 0
        rkwargs = len(argspec[4]) if argspec[4] is not None else 0
        no_sender_args = args[1:]
        if rkwargs > 0:
            kwargs = {argspec[4][0]: ' '.join(no_sender_args[pos_args:])}
            if kwargs[argspec[4][0]] == '':
                kwargs = None
            [args.pop() for arg in no_sender_args[pos_args:]]
        try:
            if kwargs is not None:
                self.func(*args, **{str(k): v for k, v in kwargs.items()})
            else:
                self.func(*args)
        except Exception as error:
            return self.plugin.events['on_command_error'](self, sender, argcopy, error)
        self.plugin.events['after_command_invoke'](self, sender, argcopy)



def on_command_error(command, sender, args, error):
    print(f"Ignoring exception in {command.name}:")
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def before_command_invoke(command, sender, args):
    pass

def after_command_invoke(command, sender, args):
    pass
    
class Plugins:
    def __init__(self):
        self.commands_str = []
        self.removed = []
        self.commands = []
        self.removed_str = []
        self.events = {
            'on_command_error': on_command_error,
            'before_command_invoke': before_command_invoke,
            'after_command_invoke': after_command_invoke
        }
        self.valid_events = ['on_command_error', 'before_command_invoke', 'after_command_invoke']

    def command(self, **kwargs):
        def decorator(function):
            name = kwargs.get('name')
            description = inspect.cleandoc(kwargs.get('description', 'No description'))
            usage = kwargs.get('usage')
            argspec = inspect.getfullargspec(function)
            if argspec[1] is not None and len(argspec[4]) > 0:
                raise TypeError("More than one keyword-only argument was provided.")
            if len(argspec[4]) > 1:
                raise TypeError("More than one keyword-only argument was provided.")
            command = Commands()
            if usage is None:
                if not inspect.ismethod(function):
                    _sig = str(inspect.signature(function)).replace("(", '').replace(")", '').split(', ')
                    del _sig[0]
                else:
                    _sig = str(inspect.signature(function)).replace("(", '').replace(")", '').split(', ')
                    del _sig[0]
                    del _sig[0]
                sig = []
                for i in _sig:
                    if i == '*':
                        continue
                    if '=' in i:
                        if '*' in i:
                            i = f"[{i.split('=')[0]}...]".replace('*', '')
                        else:
                            i = f"[{i.split('=')[0]}]"
                    else:
                        if '*' in i:
                            i = f"<{i}...>".replace('*', '')
                        else:
                            i = f"<{i}>"
                    sig.append(i)
                usage = ' '.join(sig)
            command.usage = usage 
            if not isinstance(name, str) and name is not None:
                raise TypeError('Name of a command must be a string.')
            if name is not None:
                command.name = name
            else:
                command.name = function.__name__
            command.description = description
            command.func = function
            command.plugin = self
            self.commands_str.append(command.name)
            self.commands.append(command)
        return decorator

    def event(self, **kwargs):
        def decorator(function):
            event = kwargs.get('event')
            if not isinstance(event, str) and event is not None:
                raise TypeError("Event name must be a string.")
            if event is None:
                event = function.__name__
            if event not in self.valid_events:
                raise AttributeError("Invalid event.")
            self.events[event] = function
        return decorator

    def cleanup(self):
        for command in self.commands_str:
            CommandManager.deleteCommand(command)
        for command in self.removed:
            CommandManager.registerCommand(command)
    
    def startup(self):
        for command in self.commands:
            if CommandManager.isCommand(command.name):
                cmd = CommandManager.getCommand(command.name)
                CommandManager.deleteCommand(command.name)
                self.removed_str.append(cmd.name)
                self.removed.append(cmd)
            CommandManager.registerCommand(command)

