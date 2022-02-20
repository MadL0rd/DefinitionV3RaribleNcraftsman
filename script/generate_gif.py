import os
import imageio

def start():
    filenames = os.listdir("./output/images")[:20]

    frames = []
    for filename in filenames:
        frames.append(imageio.imread("output/images/" + filename))

    # Save them as frames into a gif 
    exportname = "output/example.gif"
    imageio.mimsave(exportname, frames, format='GIF', duration=0.65)