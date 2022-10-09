import os
from pathlib import Path
import requests
import pickle
from argparse import ArgumentParser

parser = ArgumentParser(description='Role embeddings parser')

parser.add_argument('--role_descriptions', type=Path, default='../roles_description/')
parser.add_argument('--output_path', type=Path, default='../role_embeddings/role_embeddings.pkl')

args = parser.parse_args()

roles = {}

for filename in os.listdir(args.role_descriptions):
    file_path = os.path.join(args.role_descriptions, filename)
    if os.path.isfile(os.path.join(args.role_descriptions, filename)):
        with open(file_path, 'r') as f:
            role_name = Path(file_path).stem
            desc = f.read()
            roles[role_name] = desc

roles_desc = roles.items()

json = {
    'news': [item[1] for item in roles_desc]
}

embeddings = eval(requests.post("http://127.0.0.1:8080/get_embeddings", json=json).text)

roles = {role_info[0]: emb for role_info, emb in zip(roles_desc, embeddings)}


with open(args.output_path, 'wb') as f:
    pickle.dump(roles, f)

# with open(args.output_path, 'rb') as f:
#     roles_list = pickle.load(f)
