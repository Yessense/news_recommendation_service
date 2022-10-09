import os
from pathlib import Path
import requests
import pickle

roles = {}
dirpath = './roles_description/'

for filename in os.listdir(dirpath):
    file_path = os.path.join(dirpath, filename)
    if os.path.isfile(os.path.join(dirpath, filename)):
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


output_filename = '../role_embeddings/role_embeddings.pkl'
with open(output_filename, 'wb') as f:
    pickle.dump(roles, f)

if __name__ == '__main__':
    output_filename = '../role_embeddings/role_embeddings.pkl'
    with open(output_filename, 'rb') as f:
        roles_list = pickle.load(f)



