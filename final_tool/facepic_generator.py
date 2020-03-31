import csv
import os
import sys

import pickle
import cv2
import PIL
#import dnnlib.tflib as tflib
import numpy as np
import deeplab_tools
from tqdm import tqdm
from PIL import Image

DEEPLAB_MODEL_PATH = 'deeplab/deeplabv3_pascal_train_aug_2018_01_04.tar.gz'
STYLEGAN_MODEL_PATH ='network-snapshot-011265.pkl'
TRUNCATION_PSI = 0.7

def generate_single_face(Gs, deeplab_model):
    """
    Generate and return a single random face cut out with deeplab
    """
    # rnd = np.random.RandomState(None)
    # latents = rnd.randn(1, Gs.input_shape[1])
    # fmt = dict(func=tflib.convert_images_to_uint8, nchw_to_nhwc=True)
    # images = Gs.run(latents, None, truncation_psi=TRUNCATION_PSI, randomize_noise=True, output_transform=fmt)
    TEMP_IMAGE = Image.open('test.png')
    im = deeplab_model.trim(TEMP_IMAGE)
    im = cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA)
    im = PIL.Image.fromarray(im)
    return im


def generate_faces_from_csv(players, output_directory):
    """
    Generate and save facepics with
    """
    with open(STYLEGAN_MODEL_PATH, 'rb') as f:
        #_G, _D, Gs = pickle.load(f)
        Gs = ""
        deeplab_model = deeplab_tools.DeepLabModel(DEEPLAB_MODEL_PATH)
        os.makedirs(output_directory, exist_ok=True)
        print("Generating faces. Please wait.")
        for player in tqdm(players):
            im = generate_single_face(Gs, deeplab_model)
            png_filename = os.path.join(output_directory, player)
            im.save(png_filename)


def get_players_without_faces(players_csv_path, player_pics_paths):
    players_list = []

    with open(players_csv_path, newline='', encoding='UTF-8', errors='ignore') as players_csv:
        players = csv.reader(players_csv, delimiter=',')
        for player in players:
            filename = player[1] + '_' + player[2] + '_' + player[3].replace('.', '_') + '.png'
            players_list.append(filename)
            for path in player_pics_paths:
                if os.path.isfile(os.path.join(path, filename)):
                    try:
                        players_list.remove(filename)
                    except:
                        continue

    return players_list


def main():
    print("Welcome to the EHM facepic generator.")
    while True:
        players_csv_path = input("Please enter the absolute path your players .csv file: ")
        if os.path.exists(players_csv_path):
            break
        else:
            print(f"File at {players_csv_path} does not exist. Please double check that you entered the path correctly.")

    player_pics_paths = []
    path_entered = False

    while True:
        if path_entered:
            print("You have selected path(s):")
            for path in player_pics_paths:
                print(path)
        print("Please enter a path to a directory containing facepics (likely at least EHM/data/pictures/players).")
        player_pics_path = input("Or hit enter if you're done entering paths: ")
        if player_pics_path == '':
            break
        if os.path.isdir(player_pics_path):
            player_pics_paths.append(player_pics_path)
            path_entered = True
        else:
            print(f"Directory at {player_pics_path} does not exist. Please double check that you entered the path correctly.")

    players = get_players_without_faces(players_csv_path, player_pics_paths)

    while True:
        output_path = input("Please enter a path to where you want facepics to be saved (likely EHM/data/pictures/players): ")
        if os.path.isdir(output_path):
            break
        else:
            print(f"Directory at {output_path} does not exist. Please double check the path.")

    print(f"Generating {len(players)} faces will take up approximately {(len(players)*50)*0.001} MB. Do you wish to continue?")
    while True:
        cont = input("Do you wish to continue? Y/N:")
        if cont == "N":
            sys.exit(0)
        elif cont == "Y":
            break

    generate_faces_from_csv(players, output_path)
    sys.exit(0)

main()