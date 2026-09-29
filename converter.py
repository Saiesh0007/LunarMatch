from pds4_tools import pds4_read
from PIL import Image
import numpy as np

xml_file = "/home/siddharth/Desktop/Projects/Hackathon/LunarMatch/DATA/OHRC(Optical High Resolution Camera)/data/calibrated/20260103/ch2_ohr_ncp_20260103T0609041371_d_img_d18.xml"

print("Reading lunar data matrix...")
structures = pds4_read(xml_file)
image_array = structures[0].data


image_min = image_array.min()
image_max = image_array.max()
normalized_array = ((image_array - image_min) / (image_max - image_min) * 255).astype(np.uint8)

img = Image.fromarray(normalized_array, mode='L')
img.save("converted_moon_surface.png")

print("Success! Your image is saved as 'converted_moon_surface.png' in this folder.")
