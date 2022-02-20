import os
import generate_gif as gif
import prepare_files_from_config as restore
import generate_collection as generator
import upload_collection as uploader
import generate_dapp as dapp_generator
import shutil


def main():
    print("Restore from config")
    restore.start()

    # print("Generate collection")
    # generator.start()

    # print("Gif generating")
    # gif.start()

    # print("Uploading")
    # uploader.start()
    
    print("DAPP generation")
    dapp_generator.start()

    # print("Remove tmp folders")
    # shutil.rmtree("restored", ignore_errors=True)
    # shutil.rmtree("output", ignore_errors=True)

    print("Done")

if __name__ == '__main__':
    main()