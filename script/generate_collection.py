from PIL import Image
import cv2
import matplotlib.pyplot as plt
from random import sample, randint, shuffle
import random
from itertools import permutations
import itertools
import os
from pathlib import Path
from datetime import datetime

import numpy as np
import imageio

import json
from pydantic import BaseModel
from typing import Union

def start():
    # Load
    info_folder = Path("restored/info")
    path_to_rarity_layers = Path("info/rarity")

    with open(info_folder / "config.json", "r") as read_file:
        config = json.load(read_file)
        
    with open(info_folder / "meta.json", "r") as read_file:
        info_meta = json.load(read_file)

    output_dir_image = Path("output/images")
    output_dir_meta = Path("output/metadata")

    collection_name = config['collectionName']
    output_path_url = "https://storage.ncraftsman.com/" + collection_name + "/"

    output_dir_image.mkdir(parents=True, exist_ok=True)
    output_dir_meta.mkdir(parents=True, exist_ok=True)

    # Rarity

    rarity_empty = "empty" # only for one layer
    rarity_shabby = "shabby"
    rarity_normal = "normal"
    rarity_rare = "rare"
    rarity_epic = "epic"
    rarity_unique = "unique"

    def get_rarity(file_name):
        if rarity_unique in file_name:
            return rarity_unique
        if rarity_epic in file_name:
            return rarity_epic
        if rarity_rare in file_name:
            return rarity_rare
        
        if rarity_empty in file_name:
            return rarity_shabby
        if rarity_shabby in file_name:
            return rarity_shabby
        
        return rarity_normal

    class RarityCounter:
        have_rarity_shabby = False
        have_rarity_normal = False
        have_rarity_rare = False
        have_rarity_epic = False
        have_rarity_unique = False
        
        rarity_shabby_count = 0
        rarity_normal_count = 0
        rarity_rare_count = 0
        rarity_epic_count = 0
        rarity_unique_count = 0
        
        def __init__(self, layers_combination):
            for current_layer in layers_combination:
                if current_layer.params.rarity == rarity_shabby:
                    self.have_rarity_shabby = True
                    self.rarity_shabby_count =  self.rarity_shabby_count + 1
                    
                if current_layer.params.rarity == rarity_normal:
                    self.have_rarity_normal = True
                    self.rarity_normal_count = self.rarity_normal_count + 1
                    
                if current_layer.params.rarity == rarity_rare:
                    self.have_rarity_rare = True
                    self.rarity_rare_count = self.rarity_rare_count + 1
                    
                if current_layer.params.rarity == rarity_epic:
                    self.have_rarity_epic = True
                    self.rarity_epic_count = self.rarity_epic_count + 1
                    
                if current_layer.params.rarity == rarity_unique:
                    self.have_rarity_unique = True
                    self.rarity_unique_count = self.rarity_unique_count + 1

    # image model 

    class ImageParams(BaseModel):
        path: Union[str, Path]
        is_gif: bool = False
        is_colorable: bool = True        
        is_countable: bool = False
        show_meta: bool = True
        count: int = 0
        rarity: str = "normal"
        weight: int = 1 # for random sampling (P = weight / sum(weights))

        layer_name: str
        public_name: str

    # TODO separate to two classes: single image class and gif class
    class ImageModel:
        def load_image(self):
            if self.params.is_gif:
                gif = imageio.get_reader(self.params.path)
                self.iter_gif = iter(gif)
                self.num_frames = len(gif)
                self.image = next(iter(gif))
            else:
                img = cv2.imread(self.params.path, cv2.IMREAD_UNCHANGED)
                self.image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
                
            self.pil_image = Image.fromarray(self.image)
        
        def __init__(self, params: ImageParams):
            self.params = params
            self.shifting_h_value = randint(0, 180)
            
            self.load_image()
            
        def update_image_gif(self):
            self.image = next(self.iter_gif)
            self.pil_image = Image.fromarray(self.image)
            
        def reset_image_gif(self):
            gif = imageio.get_reader(self.params.path)
            self.iter_gif = iter(gif)

        def get_image(self, update_color=True):
            img_ = cv2.cvtColor(self.image, cv2.COLOR_RGBA2RGB)
            hsv = cv2.cvtColor(img_, cv2.COLOR_RGB2HSV)
            h, s, v = cv2.split(hsv)

            if update_color:
                self.shifting_h_value = randint(0, 180)
            else:
                self.shifting_h_value = 0
            
            shift_h = (h + self.shifting_h_value) % 180
            shift_hsv = cv2.merge([shift_h, s, v])
            shift_img = cv2.cvtColor(shift_hsv, cv2.COLOR_HSV2RGB)
            
            return shift_img

    # Function 
    def fixpath(path):
        return str(path).replace("\\", "/")

    def layers_combination_rarity_is_valid(layers_combination):
        counter = RarityCounter(layers_combination)
        if (counter.have_rarity_unique | counter.have_rarity_epic) & counter.have_rarity_shabby:
            return False
        if counter.rarity_unique_count > 1:
            return False
        if (counter.rarity_unique_count > 0) & (counter.rarity_epic_count > 0):
            return False
        return True


    def get_random_image(layer) -> ImageModel:
        weights = [img.params.weight for img in layer]
        probs = np.array(weights) / sum(weights)

        return np.random.choice(layer, p=probs)

    def get_random_combination(layers_for_combine):
        validation = False
        result_combination = []
        while validation == False:
            result_combination = [get_random_image(layer_image_variants) for layer_image_variants in layers_for_combine.values()]
            validation = layers_combination_rarity_is_valid(result_combination)
        
        for current_layer in result_combination:
            if current_layer.params.is_countable:
                current_layer.params.count -= 1
        
        return result_combination

    def get_layers_combination_rarity(layers_combination):
        counter = RarityCounter(layers_combination)
        
        if counter.have_rarity_unique:
            return rarity_unique
        if counter.have_rarity_epic:
            return rarity_epic
        
        if counter.rarity_rare_count > 2:
            return rarity_rare
        if counter.have_rarity_shabby > 1:
            return rarity_shabby
        
        if counter.have_rarity_rare & counter.have_rarity_shabby:
            return rarity_normal
        
        if counter.have_rarity_shabby:
            return rarity_shabby
            
        return rarity_normal

    def merge_layers(layers):
        num_frames_s = [layer.num_frames for layer in layers if layer.params.is_gif]
        if len(num_frames_s) == 0:
            pil_new_layers = []
            for layer in layers:
                if layer.params.is_colorable:
                    pil_new_layers.append(Image.fromarray(layer.get_image()))
                else:
                    pil_new_layers.append(Image.fromarray(layer.get_image(update_color=False)))

            result = pil_new_layers[0]
            for i in range(len(layers)):
                result.paste(pil_new_layers[i], (0, 0), layers[i].pil_image.convert('RGBA'))
            return result
        else:
            min_frames = min(num_frames_s)
        
            res = []
            
            for i in range(len(layers)):
                if layers[i].params.is_gif:
                    layers[i].reset_image_gif()
                    
            for index in range(min_frames):
                pil_new_layers = []
                for layer in layers:

                    if layer.params.is_gif:
                        layer.update_image_gif()

                    if layer.params.is_colorable:
                        pil_new_layers.append(Image.fromarray(layer.get_image(update_color=False)))
                    else:
                        pil_new_layers.append(Image.fromarray(layer.get_image(update_color=False)))

                result = pil_new_layers[0]
                for i in range(len(layers)):
                    result.paste(pil_new_layers[i], (0, 0), layers[i].pil_image.convert('RGBA'))
                res.append(np.array(result))
            return res
        
    def get_attributes(layers_combination):
        attributes = []
        for layer in layers_combination:
            attributes.append(
                {
                    "trait_type": layer.params.layer_name,
                    "value": layer.params.public_name,
                }
            )
            
        return attributes

    now = datetime.now()
    date_time = now.strftime("%m-%d-%Y, %H:%M:%S")
    date_day = now.strftime("%Y-%m-%d")

    print("date and time:",date_day)

    def create_post_file(index, rarity):
        with open(f"../site/_larry/{date_day}-larry_{index + 1}.md", "w") as file:
            file.write(f"""---
    layout: post
    title: Larry the booze lemur {i + 1} ({rarity})
    img: larry_{index + 1}.png
    date: 2017-07-03 12:55:00 +0300
    description: kek
    tag: [Larry, First generation, {rarity}]
    ---""")
            
    def create_picture_page_file(index, rarity):
        with open(f"../site/_posts/{date_day}-larry_{i + 1}.md", "w") as file:
            file.write(f"""---
    layout: post
    title: Larry the booze lemur {i + 1} ({rarity})
    img: larry/larry_{index + 1}.png
    date: 2017-07-03 12:55:00 +0300
    description: kek
    tag: [Larry, First generation, {rarity}]
    ---""")

    # Run precessing

    imageparams = [ImageParams.parse_obj(info) for info in info_meta]
    imagemodels = [ImageModel(params) for params in imageparams]

    rarity_images_dictionary = {}
    rarity_list = [rarity_shabby, rarity_normal, rarity_rare, rarity_epic, rarity_unique]
    for rarity in rarity_list:
        file_path = Path(path_to_rarity_layers, f"{rarity}NC.png")
        params = ImageParams(path=str(file_path.resolve()), 
                            layer_name="rarity", 
                            public_name=rarity, 
                            is_colorable=False)
        rarity_images_dictionary[rarity] = ImageModel(params)

    layers = dict()
    for layer_name in config["layers_order"]:
        layers[layer_name] = []
        for imagemodel in imagemodels:
            if imagemodel.params.layer_name == layer_name:
                layers[layer_name].append(imagemodel)

    combs = []
    generation_count = int(config["generationCount"])
    for _ in range(generation_count):
        combs.append(get_random_combination(layers))
        for k, v in layers.items():
            layers[k] = [image for image in v if not image.params.is_countable or image.params.count != 0]

    
    shuffle(combs)

    comb_metas = []

    for i, comb in enumerate(combs, start=1):
        if i % 10 == 0:
            print(i)
        
        merge_rarity = get_layers_combination_rarity(comb)
        if config["showRarity"]:
            comb.append(rarity_images_dictionary[merge_rarity])
        
        merged = merge_layers(comb)
        
        if type(merged) is list:
            filename = f"{i}.gif"
            imageio.mimsave(output_dir_image / filename, merged)
        else:
            filename = f"{i}.png"
            merged.save(output_dir_image / filename)
            
        image_path_url = output_path_url + "images/" + filename

        comb_meta = {
            "name": f"{collection_name} #{i}",
            "description": "Soon we will reveal this secret and you will see your horny cupid and a fortune card\nMore at http://www.horny-cupids.space/",
            "image": image_path_url,
            "attributes": get_attributes(comb),
        }
        
        comb_metas.append(comb_meta)
        with open((output_dir_meta / filename).with_suffix('.json'), "w") as file:
            json.dump(comb_meta, file, indent=4)

    with open(output_dir_meta / "all_meta.json", "w") as file:
        json.dump(comb_metas, file, indent=4)