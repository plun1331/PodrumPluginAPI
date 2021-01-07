# PodrumPluginAPI
 A simple 'API' that can be used for making Podrum plugins.

Podrum is currently a work in progress, and is currently useless.

# How to Install
 To install, simply download the `PluginAPI.zip` file from the latest release and insert it into your Podrum server's `src` folder.

 You can then import the module using `import PluginAPI`.

# How to Use
 First you must import and initialise the `PluginAPI.Plugins` class, which will be used to 'manage' your plugin.

 ```py
 import PluginAPI

 plugin = PluginAPI.Plugins()
 ```

## Making Commands
Making commands is very simple. Simply create a function with the `@plugin.command()` decorator.

This decorator can take 3 kwargs, `name`, `description` and `usage`.

`name` will set the command name, which defaults to the decorated function's name.

`description` will set the command description, which defaults to 'No description.'

`usage` will set the command usage, which defaults to something like the signature of the function.

Commands must always take `sender` as their first argument.

Example using all the available options:
```py
import PluginAPI

plugin = PluginAPI.Plugins()

@plugin.command(
    name = "help",
    description = "send help",
    usage = "<thing you need help with>"
)
def _help(sender, thing):
    sender.sendMessage(f"I need help with {thing}!")
```

```
Input:
    help change lightbulb
Output:
    I need help with change!
```

Setting default arguments will also work.

```py
import PluginAPI

plugin = PluginAPI.Plugins()

@plugin.command(
    name = "help",
    description = "send help",
    usage = "<me/you> <thing you need help with>"
)
def _help(sender, person="I", *, thing="Nothing"):
    sender.sendMessage(f"{person} need help with {thing}!")
```

```
Input:
    help
Output:
    I need help with Nothing!
```

If your command must take an undefined number of arguments, you can simply turn that argument into a kwarg, a keyword argument, and the rest of the commands arguments will become that keyword argument.

And no, you cannot have more than one kwarg.

```py
import PluginAPI

plugin = PluginAPI.Plugins()

@plugin.command(
    name = "help",
    description = "send help",
    usage = "<me/you> <thing you need help with>"
)
def _help(sender, person, *, thing):
    sender.sendMessage(f"{person} need help with {thing}!")
```

```
Input:
    help me change lightbulb
Output:
    Me need help with change lightbulb!
```


## Listening to events
If you want your plugin to do things when certain things happen, you should use the `events` part of the PluginAPI.

Simply create a function with the `@plugin.event()` decorator. The decorator takes one kwarg, `event`, which defaults to the function name.

You can only listen to the following events:

- `on_command_error` - Called when a command raises an exception.

- `before_command_invoke` - Called before a command is executed.

- `after_command_invoke` - Called after a command is executed.

All events take the arguments `command`, the command being invoked, `sender`, the person who invoked the command, and `args`, a list of arguments the command was invoked with.

The first item in `args` will always be the command name.

`on_command_error` takes one additional argument, `error`, the exception that was raised.

Example error handler:
```py
import PluginAPI

plugin = PluginAPI.Plugins()

@plugin.event(
    event = "on_command_error"
)
def errorHandler(command, sender, args, error):
    sender.sendMessage(f"Oops, the command broke.")
```

## Loading your plugin
So, you've made commands and event listeners, but they do nothing!

This is because you need to tell your plugin class that your plugin has actually been loaded.

To do this, simply call `plugin.startup()` when your plugin enabled. This will register your commands and listeners with the server.

Likewise, when you disable the plugin, you must call `plugin.cleanup()`. This will remove your commands and listeners from the server.

# Some things to note
You will not be warned if you make a duplicate command, it will simply replace the existing one. It will, however, reinstate the removed command when the plugin is unloaded.