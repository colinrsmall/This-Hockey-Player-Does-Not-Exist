from pathlib import Path
from tqdm import tqdm
import pandas as pd

faces_dir = Path('/Users/colinrsmall/Downloads/content/faces')
player_list = pd.read_csv('/Users/colinrsmall/Downloads/players_&_non-players.csv', encoding='ISO-8859-1')
generated_player_list = pd.read_csv('/Users/colinrsmall/Downloads/EHM_PG_v11.2.csv', encoding='ISO-8859-1')

def sort_faces():
    pathlist = Path(faces_dir).rglob('*.png')
    for path in tqdm(pathlist):
        first, last, dob = path.split('/')[-1].split('_')[0:3]

