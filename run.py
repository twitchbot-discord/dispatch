from dotenv import load_dotenv
from os import getenv

assert load_dotenv()

import dispatch
dispatch.app.run('0.0.0.0', port=80)
