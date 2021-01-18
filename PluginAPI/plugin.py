# External Modules
import inspect
from podrum.command.CommandManager import CommandManager
import traceback
import sys
import inspect
from PluginAPI.errors import CommandInvokeError, MissingRequiredArgument, TooManyArguments
from .CommandManagerEdited import CommandManager2


class Commands:
    def __init__(self):
        self.name = None
        self.description = None
        self.usage = None
        self.func = None
        self.plugin = None
    
    def execute(self, sender, args):
        # creates some variables
        arg = [sender]
        arg.extend(args[1:])
        args = arg
        argcopy = args
        
        # calls the plugin's on_command
        self.plugin.events['on_command'](self, sender, args)
        
        # parses arguments
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
        
        # convert arguments
        # signature = inspect.signature(self.func)
        # self.params = signature.parameters.copy()
        # for key, value in self.params.items():
        #     if isinstance(value.annotation, str):
        #         self.params[key] = value = value.replace(annotation=eval(value.annotation, function.__globals__))

        # invokes the command
        try:
            if kwargs is not None:
                self.func(*args, **{str(k): v for k, v in kwargs.items()})
            else:
                self.func(*args)
        except Exception as error:
            # encountered an error
            return self.plugin.events['on_command_error'](self, sender, argcopy, error)

        # calls the plugins on_command_complete
        self.plugin.events['on_command_complete'](self, sender, argcopy)



def on_command_error(command, sender, args, error):
    print(f"Ignoring exception in {command.name}:")
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def on_command(command, sender, args):
    pass

def on_command_complete(command, sender, args):
    pass
    
class Plugins:
    def __init__(self):
        self.commands_str = []
        self.removed = []
        self.commands = []
        self.removed_str = []
        self.events = {
            'on_command_error': on_command_error,
            'on_command': on_command,
            'on_command_complete': on_command_complete
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

    def unload(self):
        for command in self.commands_str:
            CommandManager2.deleteCommand(command)
        for command in self.removed:
            CommandManager.registerCommand(command)
    
    def load(self):
        for command in self.commands:
            if CommandManager.isCommand(command.name):
                cmd = CommandManager.getCommand(command.name)
                CommandManager2.deleteCommand(command.name)
                self.removed_str.append(cmd.name)
                self.removed.append(cmd)
            CommandManager.registerCommand(command)

