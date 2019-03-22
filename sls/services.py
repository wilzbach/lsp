class ServiceRegistry():
    """
    Contains a list of all available Asyncy services
    """
    def __init__(self):
        self.services = [
            "http", "email", "slack", "log", "twitter", "twilio", "crontab",
            "yaml", "blink-diff", "uuid", "node", "jwt", "elasticsearch",
        ]

    def find_services(self, keyword):
        services = []
        for service in self.services:
            if service.startswith(keyword):
                services.append(Service(service))
        return services


class Service():
    """
    An individual service
    """
    def __init__(self, name):
        self._name = name
        self._description = f'.desc: {name}'
        self._commands = ["foo", "bar", "mar"]

    def name(self):
        return self._name

    def description(self):
        return self._description

    def commands(self):
        return self._commands

    def args_for_command(self, command):
        return [
            {
                'name': 'a parameter',
                'description': 'a parameter description',
                'type_': 'int'
            },
            {
                'name': 'b parameter',
                'description': 'b parameter description',
                'type_': 'string'
            },
        ]
