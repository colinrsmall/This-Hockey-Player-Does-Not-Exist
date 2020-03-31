import subprocess, os, sys, csv, shutil
from PIL import Image
from tqdm import tqdm
from pathlib import Path


def delete_extra_faces():
    file_names = []
    with open('player_list.csv', newline='',  encoding='utf-8') as faces_csv:
        reader = csv.reader(faces_csv, delimiter=',')
        for player in reader:
            file_name = player[0] + '_' + player[1] + '_' + player[2].replace('.', '_') + '.png'
            file_names.append(file_name)

    pathlist = Path("faces").glob('*.png')
    for path in tqdm(pathlist):
        if str(path)[6:] not in file_names:
            os.remove(str(path))


def delete_opaque_or_wrongly_sized_files(dir):
    pathlist = Path(dir).rglob('*.png')
    for path in tqdm(pathlist):
        path_str = str(path)
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
            if opaque.stdout.decode("utf-8") == 'True':
                os.remove(path)
                continue

            if size.stdout.decode("utf-8") != "157x200":
                baseheight = 200
                img = Image.open(path)
                hpercent = (baseheight / float(img.size[1]))
                wsize = int((float(img.size[0]) * float(hpercent)))
                img = img.resize((wsize, baseheight), Image.ANTIALIAS)
                img.save(path)

        except Exception as e:
            print(e)
            continue


def fill_with_purple(dir):
    pathlist = Path(dir).rglob('*.png')
    for path in tqdm(pathlist):
        path_str = str(path)
        command = f"convert -background rgb(160,160,255) -gravity south -extent 200x200 -flatten {path_str} {path_str}"
        try:
            output = subprocess.run(command.split(), stdout=subprocess.PIPE, timeout=5)
            if output.stderr is not None:
                print(output.stderr)
                print(path_str)
                continue
        except Exception as e:
            print(e)
            print(path_str)
            continue


def check_format():
    pathlist = Path("faces/purple/upscaled/expanded").glob('*.png')
    for path in tqdm(pathlist):
        path_str = str(path)
        command = f"identify {path_str}"
        try:
            output = subprocess.run(command.split(), stdout=subprocess.PIPE, timeout=5)
            if "PNG 512x512 512x512+0+0 8-bit sRGB" not in str(output.stdout):
                print("\n")
                print(str(output.stdout))
                print(path_str)
        except Exception as e:
            print(e)
            print(path_str)
            continue


def resize_down():
    pathlist = Path("/Users/colinrsmall/Downloads/content/results").glob('*.png1')
    for path in tqdm(pathlist):
        path_str = str(path)
        command = f"convert {path_str} -resize 200x200 {path_str.split('.')[0]}1.png"
        try:
            subprocess.run(command.split(), stdout=subprocess.PIPE, timeout=5)
        except Exception as e:
            print(e)
            print(path_str)
            continue
        # command = f"convert {path_str} -crop 157x200 -gravity south {path_str}"
        # try:
        #     subprocess.run(command.split(), stdout=subprocess.PIPE, timeout=5)
        # except Exception as e:
        #     print(e)
        #     print(path_str)
        #     continue


def convert_to_rgb():
    pathlist = Path("/Users/colinrsmall/Desktop/EHM_Faces/faces/filtered/junior/upscaled").glob('*.png')
    for path in tqdm(pathlist):
        path_str = str(path)
        command = f"convert {path_str} -alpha remove {path_str}"
        try:
            subprocess.run(command.split(), stdout=subprocess.PIPE, timeout=5)
        except Exception as e:
            print(e)
            print(path_str)
            continue


def create_names_nationality_map():
    map = {}
    with open('players_countries_ages.csv', newline='', encoding='UTF-8', errors='ignore') as names_countries_file:
        names_countries = csv.reader(names_countries_file, delimiter=',')
        for player in names_countries:
            filename = player[0] + '_' + player[1] + '_' + player[2].replace('.', '_') + '.png'
            map[filename] = player[3]
    return map


def create_age_map():
    map = {}
    with open('players_countries_ages.csv', newline='', encoding='UTF-8', errors='ignore') as names_countries_file:
        names_countries = csv.reader(names_countries_file, delimiter=',')
        for player in names_countries:
            filename = player[0] + '_' + player[1] + '_' + player[2].replace('.', '_') + '.png'
            map[filename] = player[2].split('.')[2]
    return map

def filter_face_by_age(path, age_map, base_dir):
    filename = str(path).split('/')[-1]
    if filename in age_map.keys():
        age = int(age_map[filename])
        if 2020-age < 18:
            dir = base_dir + '/U18/'
            os.makedirs(dir, exist_ok=True)
            shutil.copy2(path, dir + filename)
        if 2020 - age < 21:
            dir = base_dir + '/U21/'
            os.makedirs(dir, exist_ok=True)
            shutil.copy2(path, dir + filename)
        elif 2020 - age < 24:
            dir = base_dir + '/U24/'
            os.makedirs(dir, exist_ok=True)
            shutil.copy2(path, dir + filename)
        elif 2020 - age < 28:
            dir = base_dir + '/U28/'
            os.makedirs(dir, exist_ok=True)
            shutil.copy2(path, dir + filename)
        elif 2020 - age < 32:
            dir = base_dir + '/U32/'
            os.makedirs(dir, exist_ok=True)
            shutil.copy2(path, dir + filename)
        elif 2020 - age < 42:
            dir = base_dir + '/old/'
            os.makedirs(dir, exist_ok=True)
            shutil.copy2(path, dir + filename)
        else:
            dir = base_dir + '/too_old/'
            os.makedirs(dir, exist_ok=True)
            shutil.copy2(path, dir + filename)

def filter_faces():
    BASE_DIR = '/Users/colinrsmall/Desktop/EHM_Faces/faces'
    nordic_countries = ['Sweden', 'Denmark', 'Norway']
    generic_european_countries = ['Austria', 'Belgium', 'France', 'Germany', 'Great Britain', 'Italy', 'Netherlands',
                                  'Poland', 'Switzerland', 'Turkey', 'Wales']
    slavic_countries = ['Croatia', 'Czech Republic', 'Hungary', 'Slovakia', 'Slovenia']
    finnish_countries = ['Finland', 'Estonia', 'Latvia', 'Lithuania']
    eastern_european_countries = ['Belarus', 'Kazakhstan', 'Ukraine', 'Russia']
    asian_countries = ['China', 'Japan']
    north_american_countries = ['Uinted States', 'Canada']
    country_map = create_names_nationality_map()
    age_map = create_age_map()
    pathlist = Path('/Users/colinrsmall/Library/Application Support/CrossOver/Bottles/Steam/drive_c/Program Files (x86)/Steam/steamapps/workshop/content/301120/1896655252/').rglob('*.png')
    for path in tqdm(pathlist):
        filename = str(path).split('/')[-1]
        if filename in country_map.keys():
            country = country_map[filename]
            if country in nordic_countries:
                dir = BASE_DIR + '/filtered/nordic/'
                filter_face_by_age(path, age_map, dir)
            elif country in generic_european_countries:
                dir = BASE_DIR + '/filtered/generic_european/'
                filter_face_by_age(path, age_map, dir)
            elif country in slavic_countries:
                dir = BASE_DIR + '/filtered/slavic/'
                filter_face_by_age(path, age_map, dir)
            elif country in finnish_countries:
                dir = BASE_DIR + '/filtered/finnish/'
                filter_face_by_age(path, age_map, dir)
            elif country in eastern_european_countries:
                dir = BASE_DIR + '/filtered/eastern_european/'
                filter_face_by_age(path, age_map, dir)
            elif country in asian_countries:
                dir = BASE_DIR + '/filtered/asian/'
                filter_face_by_age(path, age_map, dir)
            elif country in north_american_countries:
                dir = BASE_DIR + '/filtered/north_american/'
                filter_face_by_age(path, age_map, dir)
            else:
                dir = BASE_DIR + '/filtered/other/'
                filter_face_by_age(path, age_map, dir)


def get_players_without_faces():
    players = []
    images_path = '/Users/colinrsmall/Library/Application Support/CrossOver/Bottles/Steam/drive_c/Program Files (x86)/Steam/steamapps/workshop/content/301120/1896655252/'
    with open('junior_players.csv', newline='', encoding='UTF-8', errors='ignore') as junior_players:
        names_countries = csv.reader(junior_players, delimiter=',')
        for player in names_countries:
            filename = player[0] + '_' + player[1] + '_' + player[2].replace('.', '_') + '.png'
            if not os.path.isfile(os.path.join(images_path, filename)):
                players.append(filename)

    with open('output.csv', 'w+', newline='', errors='ignore') as output_file:
        wr = csv.writer(output_file)
        wr.writerow(players)

    return map


# delete_opaque_or_wrongly_sized_files()
# fill_with_purple()
#convert_to_rgb()
#get_players_without_faces()
filter_faces()
delete_opaque_or_wrongly_sized_files('faces/filtered')
fill_with_purple('faces/filtered')
sys.exit(0)
