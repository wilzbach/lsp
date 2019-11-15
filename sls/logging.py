import logging

# more detailed logs for sls only
sls_logger = logging.getLogger("sls")
sls_logger.setLevel(logging.DEBUG)


def configure_logging(with_stdio):
    # set the default level to INFO
    handlers = [
        logging.FileHandler("lsp.log"),
    ]
    if with_stdio:
        handlers.append(logging.StreamHandler())
    logging.basicConfig(level=logging.INFO, handlers=handlers)


def logger(name):
    # remove root_module name as its already included
    # in the sls_logger
    name = ".".join((name.split(".")[1:]))
    return sls_logger.getChild(name)
