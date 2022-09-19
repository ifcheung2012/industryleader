from importlib import import_module
from app import app, server
from environment.settings import APP_HOST, APP_PORT, APP_DEBUG, DEV_TOOLS_PROPS_CHECK

import os

#动态导入pages目录下所有callback模块
modules = []
for parent,dirnames,filenames in os.walk('pages'):
    for filename in filenames:
        if filename.endswith('callback.py'):
            modules.append(os.path.join(parent,filename).replace('.py','').replace('/','.'))

imported_modules={p:import_module(p) for p in modules}

if __name__ == '__main__':
    app.run_server(debug=True,port=8058)