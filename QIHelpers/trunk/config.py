import os
PROJECT_NAME = 'ZetaUtils'
SKINS_DIR = 'skins'
ihome = os.environ.get('INSTANCE_HOME', '')
SKINS_PATH = os.path.join(ihome,'Products',PROJECT_NAME,SKINS_DIR)

GLOBALS = globals()