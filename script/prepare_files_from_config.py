from pathlib import Path
import json
import base64

def start():
    path_raw_config_folder = Path("raw_config")
    path_restore_info_string = "restored/info"
    path_restore_info = Path(path_restore_info_string)
    path_restore_materials_string = "restored/materials"
    path_restore_materials = Path(path_restore_materials_string)

    path_restore_info.mkdir(parents=True, exist_ok=True)
    path_restore_materials.mkdir(parents=True, exist_ok=True)

    with open(path_raw_config_folder / "config.json", "r") as read_file:
        config = json.load(read_file)
        config = json.loads(config)

    info_meta = config['meta']
    config = config['config']

    def restore_image(img_data):
        index = img_data['imageBase64'].find(';base64')
        extension = img_data['imageBase64'][:index]
        extension = extension[extension.find('/') + 1:]
        img_base64 = img_data['imageBase64'][index + 8:]
        img_name = img_data['layer_name'] + '_' + img_data['public_name']
        img2save_name = img_name + '.' + extension
        path2save = path_restore_materials_string + '/' + img2save_name

        imgdata = base64.b64decode(img_base64)
        with open(path2save, "wb") as fh:
            fh.write(imgdata)

        return path2save

    for index, img_data in enumerate(info_meta):
        path = restore_image(img_data)
        del info_meta[index]['imageBase64']
        info_meta[index]['path'] = path
    
    with open(path_restore_info_string + '/meta.json', 'w') as f:
        json.dump(info_meta, f)

    with open(path_restore_info_string + '/config.json', 'w') as f:
        json.dump(config, f)