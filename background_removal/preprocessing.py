import subprocess, os, sys, csv, shutil, random
from tqdm import tqdm
from pathlib import Path

def delete_opaque_or_wrongly_sized_files():
    pathlist = Path('/Users/colinrsmall/Library/Application Support/CrossOver/Bottles/Steam/drive_c/Program Files (x86)/Steam/steamapps/workshop/content/301120/1896655252').glob('*.png')
    for path in tqdm(pathlist):
        path_str = str(path)
        filename = str(path).split('/')[-1]
        try:
            # Get image size
            command = ["identify", "-format", "%wx%h", f"{path_str}"]
            size = subprocess.run(command, stdout=subprocess.PIPE, timeout=5)
            if size.stderr is not None:
                print(size.stderr)
                print(path_str)
                continue

            # Get if image is opaque
            command = ["identify", "-format", "%[opaque]", f"{path_str}"]
            opaque = subprocess.run(command, stdout=subprocess.PIPE, timeout=5)
            if opaque.stderr is not None:
                print(opaque.stderr)
                print(path_str)
                continue

            # Copy file if image is not opaque and matches size
            if size.stdout.decode("utf-8") == "157x200" and opaque.stdout.decode("utf-8") != 'True':
                shutil.copy(path, '/Users/colinrsmall/Desktop/EHM_Faces/background_removal/raw_images/'+filename)

        except Exception as e:
            print(e)
            continue


def fill_with_purple():
    pathlist = Path("/Users/colinrsmall/Desktop/EHM_Faces/background_removal/raw_images").rglob('*.png')
    for path in tqdm(pathlist):
        path_str = str(path)
        filename = str(path).split('/')[-1]
        new_path = '/Users/colinrsmall/Desktop/EHM_Faces/background_removal/with_background/' + filename
        command = ['convert', '-background', 'rgb(160,160,255)', '-gravity', 'south', '-extent', '200x200', '-flatten', path_str, new_path]
        try:
            output = subprocess.run(command, stdout=subprocess.PIPE, timeout=5)
            if output.stderr is not None:
                print(output.stderr)
                print(path_str)
                continue
        except Exception as e:
            print(e)
            print(path_str)
            continue


def segment_images():
    pathlist = Path("/Users/colinrsmall/Desktop/EHM_Faces/background_removal/raw_images").rglob('*.png')
    for path in tqdm(pathlist):
        path_str = str(path)
        filename = str(path).split('/')[-1]
        new_path = '/Users/colinrsmall/Desktop/EHM_Faces/background_removal/segmented_images/' + filename
        try:
            command = ['convert', path, '-fuzz', '60%', '-fill', 'rgb(192,128,128)', '+opaque', 'none', new_path]
            output = subprocess.run(command, stdout=subprocess.PIPE, timeout=5)
            if output.stderr is not None:
                print(output.stderr)
                print(path_str)
                continue
            command = ['convert', '-background', 'black', '-gravity', 'south', '-extent', '200x200',
                       '-flatten', new_path, new_path]
            output = subprocess.run(command, stdout=subprocess.PIPE, timeout=5)
            if output.stderr is not None:
                print(output.stderr)
                print(path_str)
                continue
        except Exception as e:
            print(e)
            print(path_str)
            continue

def create_training_lists():
    val = []
    train = []
    trainval = []
    pathlist = Path("/Users/colinrsmall/Desktop/EHM_Faces/background_removal/segmented_images_raw").rglob('*.png')
    for path in tqdm(pathlist):
        filename = str(path).split('/')[-1].split('.png')[0]
        r = random.random()
        if r < 0.8:
            train.append(filename+'\n')
        else:
            val.append(filename+'\n')
        trainval.append(filename+'\n')

    with open('val.txt', 'w', encoding='UTF-8', errors='ignore') as valtxt:
        valtxt.writelines(val, )
    with open('train.txt', 'w', encoding='UTF-8', errors='ignore') as traintxt:
        traintxt.writelines(train)
    with open('valtrain.txt', 'w', encoding='UTF-8', errors='ignore') as valtraintxt:
        valtraintxt.writelines(trainval)

#delete_opaque_or_wrongly_sized_files()
#fill_with_purple()
#segment_images()
create_training_lists()
sys.exit(0)
