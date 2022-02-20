import shutil
from pathlib import Path
import json
import os, fnmatch

def start():
    info_folder = Path("restored/info")

    with open(info_folder / "config.json", "r") as read_file:
        config = json.load(read_file)

    collection_name = config['collectionName']

    dapp_path = '../static/' + collection_name
    shutil.rmtree(dapp_path, ignore_errors=True)
    shutil.copytree('DAPP/build', dapp_path)

    def findReplace(directory, find, replace, filePattern):
        for path, dirs, files in os.walk(os.path.abspath(directory)):
            for filename in fnmatch.filter(files, filePattern):
                filepath = os.path.join(path, filename)
                with open(filepath) as f:
                    s = f.read()
                s = s.replace(find, replace)
                with open(filepath, "w") as f:
                    f.write(s)

    def dapp_replace(variable, value):
        findReplace(dapp_path, variable, value, "*.html")
        findReplace(dapp_path, variable, value, "*.json")
        findReplace(dapp_path, variable, value, "*.css")
        findReplace(dapp_path, variable, value, "*.js*")

    dapp_replace("[CollectionName]", collection_name)