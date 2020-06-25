import os

# Flask settings
FLASK_DEBUG = os.environ.get if os.environ.get is not None else False
