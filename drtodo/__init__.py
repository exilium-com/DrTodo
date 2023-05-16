from importlib import metadata

__version__ = metadata.version(__package__)

del metadata  # avoids polluting the results of dir(__package__)

# see https://github.com/python-poetry/poetry/issues/273#issuecomment-1103812336
