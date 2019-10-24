from lark.exceptions import UnexpectedCharacters, UnexpectedToken

from sls.logging import logger
from sls.services.action import Action
from sls.services.argument import Argument
from sls.services.command import Command
from sls.services.service import Service

from storyscript.parser import Parser


log = logger(__name__)


class ASTAnalyzer:
    # TODO: add basic keywords
    # TODO: add existing variables
    # TODO: add existing functions

    def __init__(self, service_registry):
        self.parser = Parser()
        self.service_registry = service_registry

    def complete(self, context):
        is_space = len(context.line) > 0 and context.line[-1] == ' '
        log.debug(f"line: '{context.line}'")
        line = context.line
        if len(line.strip()) == 0:
            # start of a new line
            yield from self.complete_name()
            return
        if ':' in line:
            return
        try:
            if '=' in line:
                # try to convert assignments to expressions for now
                assignment = line.split('=')[-1]
                if len(assignment.strip()) > 0:
                    line = assignment
            ast = self.parser.parse(line, allow_single_quotes=False)
            log.debug(ast.pretty())
            yield from self.try_ast(ast, context.word, is_space)
            return
        except UnexpectedCharacters as e:
            log.error(e)
            pass
        except UnexpectedToken as e:
            if 'NAME' in e.expected:
                yield from self.complete_name()
                return
            log.error(e)

    def complete_name(self):
        # variables or services
        yield from self.get_services('')

    def try_ast(self, ast, word, is_space):
        if ast.block is not None:
            ast = ast.block
        if ast.rules is not None:
            ast = ast.rules
        if ast.service_block is not None:
            ast = ast.service_block.service
            if ast.service_fragment and \
                    ast.service_fragment.command is not None:
                service = ast.path.child(0).value
                if is_space:
                    # argument
                    command = ast.service_fragment.command.children[0].value
                    yield from self.get_arguments(service, command)
                    return

                # it's the command
                yield from self.get_commands(service)
                return
            if is_space:
                # fresh command starts here
                service = ast.path.child(0).value
                yield from self.get_commands(service)
                return
            else:
                yield from self.get_services(word)
                return

    def get_arguments(self, service_name, command_name):
        service = self.service_registry.get_service(service_name)
        if service is None:
            return

        service_config = service.configuration()

        command = service_config.command(command_name)
        if command is not None:
            for arg in command.args():
                yield Argument(arg)

        action = service_config.action(command_name)
        if action is not None:
            for arg in action.args():
                yield Argument(arg)

    def get_commands(self, service_name):
        service = self.service_registry.get_service(service_name)
        if service is None:
            return

        service_config = service.configuration()
        for command in service_config.commands():
            yield Command(command)

        for action in service_config.actions():
            yield Action(action)

    def get_services(self, word):
        services = self.service_registry.find_services(word)
        for service in services:
            yield Service(service)
