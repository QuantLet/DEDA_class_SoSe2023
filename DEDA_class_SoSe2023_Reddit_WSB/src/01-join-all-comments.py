import pandas as pd
import os

# folder path
dir_path = '../data/comments/'

# list to store files
res = []
df_l = []
# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a zip file
    if os.path.isfile(os.path.join(dir_path, path)) and path[-3:] == 'zip':
        df = pd.read_csv(dir_path + path, encoding='latin')
        df_l.append(df)
        print(f'{path} reading finished')

df_res = pd.concat(df_l)
df_res.to_csv('../data/all_comments.zip', index=False, compression='zip')

print('All comments were saved into all_comments.zip')
