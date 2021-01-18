from podrum.command.CommandManager import CommandManager


class CommandManager2:
    @staticmethod
    def deleteCommand(command):
        if command in CommandManager.commands:
            del(CommandManager.commands[command])

    @staticmethod
    def getCommand(command):
        if command in CommandManager.commands:
            return CommandManager.commands[command]
        return None

