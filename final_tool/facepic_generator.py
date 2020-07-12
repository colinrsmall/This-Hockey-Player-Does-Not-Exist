import csv
import os
import sys

import pickle
import cv2
import PIL
#import dnnlib.tflib as tflib
import numpy as np
import requests
import deeplab_tools
from tqdm import tqdm
from dnnlib import tflib
from PIL import Image
import urllib3

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

DEEPLAB_MODEL_PATH = os.path.join('models', 'deeplabv3_pascal_train_aug_2018_01_04.tar.gz')
STYLEGAN_MODEL_PATH =os.path.join('models', 'network-snapshot-011325.pkl')
TRUNCATION_PSI = 0.7

def generate_single_face(Gs, deeplab_model):
    """
    Generate and return a single random face cut out with models
    """
    rnd = np.random.RandomState(None)
    latents = rnd.randn(1, Gs.input_shape[1])
    fmt = dict(func=tflib.convert_images_to_uint8, nchw_to_nhwc=True)
    images = Gs.run(latents, None, truncation_psi=TRUNCATION_PSI, randomize_noise=True, output_transform=fmt)
    im = cv2.cvtColor(images[0], cv2.COLOR_BGRA2RGBA)
    im = PIL.Image.fromarray(im)
    im = deeplab_model.trim(im)
    return im


def generate_faces_from_csv(players, output_directory):
    """
    Generate and save facepics with
    """
    with open(STYLEGAN_MODEL_PATH, 'rb') as f:
        tflib.init_tf()
        _G, _D, Gs = pickle.load(f)
        deeplab_model = deeplab_tools.DeepLabModel(DEEPLAB_MODEL_PATH)
        os.makedirs(output_directory, exist_ok=True)
        print("Generating faces. Please wait.")
        for player in tqdm(players):
            im = generate_single_face(Gs, deeplab_model)
            png_filename = os.path.join(output_directory, player)
            im = PIL.Image.fromarray(im)
            im.save(png_filename)


def get_players_without_faces(players_csv_path, player_pics_paths):
    players_list = []

    with open(players_csv_path, newline='', encoding='ISO-8859-1', errors='ignore') as players_csv:
        players = csv.reader(players_csv, delimiter=',')
        for player in players:
            if player[8].lower() == 'player' or player[8].lower() == 'player/non-player':
                filename = player[1] + '_' + player[2] + '_' + player[3].replace('.', '_') + '.png'
                players_list.append(filename)
                for path in player_pics_paths:
                    if os.path.isfile(os.path.join(path, filename)):
                        try:
                            players_list.remove(filename)
                        except:
                            continue

    return players_list

# From: https://gist.github.com/wy193777/0e2a4932e81afc6aa4c8f7a2984f34e2
def download_from_url(url, dst):
    """
    @param: url to download file
    @param: dst place to put the file
    """
    try:
        try:
            file_size = int(requests.head(url).headers["Content-Length"])
        except:
            # Work around for missing content-length header from Google drive API
            file_size = 324000000
        if os.path.exists(dst):
            first_byte = os.path.getsize(dst)
        else:
            first_byte = 0
        if first_byte >= file_size:
            return file_size
        pbar = tqdm(
            total=file_size, initial=first_byte,
            unit='B', unit_scale=True, desc=dst)
        req = requests.get(url, stream=True)
        with(open(dst, 'ab')) as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(1024)
        pbar.close()
        return file_size
    except requests.exceptions.ConnectionError as e:
        print("Download failed. Please double check your internet connection and re-run the program.")
        if os.path.exists(dst):
            os.remove(dst)
        sys.exit(-1)


def main():
    print("Welcome to the EHM facepic generator.")

    u24 = bool(input("Would you like to generate images for U24 players or for players of all ages? 1/0: "))

    if not os.path.exists(DEEPLAB_MODEL_PATH):
        print("Downloading models cut-out model. Please wait.")
        os.makedirs('models/', exist_ok=True)
        download_from_url('http://download.tensorflow.org/models/deeplabv3_pascal_train_aug_2018_01_04.tar.gz', DEEPLAB_MODEL_PATH)

    if not os.path.exists(STYLEGAN_MODEL_PATH):
        print("Downloading U24 StyleGAN model. Please wait.")
        os.makedirs('models/', exist_ok=True)
        if u24:
            download_from_url('https://www.googleapis.com/drive/v3/files/1dNbWoeuIgHkg70L_2Ajmv3Ci5qQ3UYHd/?key=AIzaSyCSPE2HSzu2RBUX7E1Fml9lGadzsGt37w8&alt=media', STYLEGAN_MODEL_PATH)
        else:
            download_from_url('https://www.googleapis.com/drive/v3/files/1Nl_IReTP91UCJmE4chBCZE5f9YPbckRJ/?key=AIzaSyCSPE2HSzu2RBUX7E1Fml9lGadzsGt37w8&alt=media',STYLEGAN_MODEL_PATH)

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


    print("Please choose a variance level for faces:")
    print("Very Low Variance      Low Variance        High Variance     Very High Variance")
    print("<--- 0.6 ----------------- 0.7 ----------------- 0.8 ----------------- 0.9 --->")
    print("Lower variance is less prone to generating unrealistic faces but will generate more boring faces.")
    print("0.8 or 0.7 is recommended.")
    while True:
        psi = input("Variance level: ")
        try:
            TRUNCATION_PSI = float(psi)
            break
        except Exception:
            print("Please enter a number betweeen 0 and 1")


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
