'''
This script takes the csv files from count_info03.py & counts the number citations with each piece of information.

Notes
count_info03 - this includes all biblio citations (that grobid could process, ie it doesn't include citations in the _500.txt file)
'''

from pathlib import Path
import glob
import os
import pandas as pd


def meta_data_col(row):

    c1 = row['author_id'] == 1
    c2 = row['journal_id'] == 1
    c3 = row['year'] == 1
    c4 = row['volume'] + row['issue'] + row['first_page'] + row['last_page'] > 0

    if c1 and c2 and c3 and c4:
        val = 1
    else:
        val = 0
    return val


def get_both(row):

    c1 = row['title'] == 1
    c2 = row['meta_data'] == 1

    if c1 or c2:
        val = 1
    else:
        val = 0
    return val


script_name = Path(__file__).stem

path_base = 'R:/Personal/Hannah/research_projects/ml'
path_csv = os.path.join(path_base, f'from_py/count_info03')
path_output = os.path.join(path_base, f'from_py/{script_name}')
os.makedirs(path_output, exist_ok=True)

file_pattern = os.path.join(path_csv, '*.csv')
file_paths = glob.glob(file_pattern, recursive=False)

# LOOP
dfs = []
for i, file_path in enumerate(file_paths):

    print(i)
    df_i = pd.read_csv(file_path)
    df_i = df_i.drop(columns=['xml_id'])
    dfs.append(df_i)

df = pd.concat(dfs)
df = df.drop_duplicates()
df = df.drop_duplicates(subset=['md5_id'])  # This drops one row.

df['meta_data'] = df.apply(meta_data_col, axis=1)
df['title_and_or_meta_data'] = df.apply(get_both, axis=1)

counts = {col: df[col].sum() for col in df.columns if col not in ['md5_id']}  # dict with sum of each column (except md5_id)
n_biblio = df.shape[0]

df_final = pd.DataFrame([counts])

# TRANSPOSE
df_final_t = df_final.T
df_final_t = df_final_t.rename(columns={df_final_t.columns[0]: 'count'})
df_final_t['percent'] = (100 * df_final_t['count'] / n_biblio).round(2)

df_final_t.to_csv(os.path.join(path_output, 'info_counts.csv'), index=True)

print("end")
