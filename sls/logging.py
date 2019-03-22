import logging

# set the default level to INFO
handlers = [
        logging.FileHandler('lsp.log'),
        logging.StreamHandler()
]
logging.basicConfig(
    level=logging.INFO,
    handlers=handlers
)

# more detailed logs for sls only
sls_logger = logging.getLogger('sls')
sls_logger.setLevel(logging.DEBUG)


def logger(name):
    # remove root_module name as its already included
    # in the sls_logger
    name = '.'.join((name.split('.')[1:]))
    return sls_logger.getChild(name)
