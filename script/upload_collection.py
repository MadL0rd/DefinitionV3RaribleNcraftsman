from pathlib import Path
import json
import boto3
import os

def start():
    info_folder = Path("restored/info")
    path_to_rarity_layers = Path("info/rarity")

    with open(info_folder / "config.json", "r") as read_file:
        config = json.load(read_file)
        
    with open(info_folder / "meta.json", "r") as read_file:
        info_meta = json.load(read_file)

    collection_name = config['collectionName']


    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id="3PyKOMO8AWcufXM8A5-r",
        aws_secret_access_key="mdKsP322x9hzkKI8ViXC67EluPbYaU8ll7tUmV2D"
    )
    bucket_name = 'storage.ncraftsman.com'

    for image in os.listdir("./output/images"):
        print(image)
        s3.upload_file('output/images/' + image, bucket_name, collection_name + '/images/' + image)

    for metadata in os.listdir("./output/metadata"):
        print(metadata)
        s3.upload_file('output/metadata/' + metadata, bucket_name, collection_name + '/metadata/' + image)

    s3.upload_file('output/example.gif', bucket_name, collection_name + '/example.gif')
