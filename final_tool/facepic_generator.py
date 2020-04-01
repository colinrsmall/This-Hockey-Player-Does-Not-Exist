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
from PIL import Image
import urllib3

DEEPLAB_MODEL_PATH = os.path.join('models', 'deeplabv3_pascal_train_aug_2018_01_04.tar.gz')
STYLEGAN_MODEL_PATH =os.path.join('models', 'network-snapshot-011265.pkl')
TRUNCATION_PSI = 0.7

def generate_single_face(Gs, deeplab_model):
	"""
	Generate and return a single random face cut out with models
	"""
	rnd = np.random.RandomState(None)
	latents = rnd.randn(1, Gs.input_shape[1])
	fmt = dict(func=tflib.convert_images_to_uint8, nchw_to_nhwc=True)
	images = Gs.run(latents, None, truncation_psi=TRUNCATION_PSI, randomize_noise=True, output_transform=fmt)
	im = deeplab_model.trim(images[0])
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
			if player[8] == 'Player':
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
			file_size = 309000000
		if os.path.exists(dst):
			first_byte = os.path.getsize(dst)
		else:
			first_byte = 0
		if first_byte >= file_size:
			return file_size
		header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}
		pbar = tqdm(
			total=file_size, initial=first_byte,
			unit='B', unit_scale=True, desc=url.split('/')[-1])
		req = requests.get(url, headers=header, stream=True)
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

	if not os.path.exists('models/deeplabv3_pascal_train_aug_2018_01_04.tar.gz'):
		print("Downloading models cut-out model. Please wait.")
		os.makedirs('models/', exist_ok=True)
		download_from_url('http://download.tensorflow.org/models/deeplabv3_pascal_train_aug_2018_01_04.tar.gz', 'models/deeplabv3_pascal_train_aug_2018_01_04.tar.gz')

	if not os.path.exists('models/network-snapshot-011265.pkl'):
		print("Downloading StyleGAN model. Please wait.")
		os.makedirs('models/', exist_ok=True)
		download_from_url('https://www.googleapis.com/drive/v3/files/1dTueR4LvPL4P1D107kEzfL0U8VkKvbeI/?key=AIzaSyCSPE2HSzu2RBUX7E1Fml9lGadzsGt37w8&alt=media', 'models/network-snapshot-011265.pkl')

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