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
            return self.complete_name()
        if ':' in line:
            return []
        try:
            if '=' in line:
                # try to convert assignments to expressions for now
                assignment = line.split('=')[-1]
                if len(assignment.strip()) > 0:
                    line = assignment
            ast = self.parser.parse(line, allow_single_quotes=False)
            log.debug(ast.pretty())
            return self.try_ast(ast, context.word, is_space)
        except UnexpectedCharacters as e:
            log.error(e)
            pass
        except UnexpectedToken as e:
            if 'NAME' in e.expected:
                return self.complete_name()
            log.error(e)
        return []

    def complete_name(self):
        # variables or services
        return self.get_services('')

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
                    return self.get_arguments(service, command)

                # it's the command
                return self.get_commands(service)
            if is_space:
                # fresh command starts here
                service = ast.path.child(0).value
                return self.get_commands(service)
            else:
                return self.get_services(word)
        return []

    def get_arguments(self, service_name, command_name):
        service = self.service_registry.get_service(service_name)
        if service is None:
            return []
        service_config = service.configuration()
        command = service_config.command(command_name)
        action = service_config.action(command_name)
        result = []
        if command is not None:
            result.extend(command.args())
        if action is not None:
            result.extend(action.args())
        return [Argument(arg) for arg in result]

    def get_commands(self, service_name):
        service = self.service_registry.get_service(service_name)
        if service is None:
            return []
        service_config = service.configuration()
        return [
            *[Command(command) for command in service_config.commands()],
            *[Action(action) for action in service_config.actions()],
        ]

    def get_services(self, word):
        services = self.service_registry.find_services(word)
        return [Service(service) for service in services]
