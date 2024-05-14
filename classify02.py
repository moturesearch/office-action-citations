'''
This code creates one csv file for each tsv file (that Emma gave me). Emma classified the citations.
The csv file contains two columns: label, md5_id. The csv file only contains biblio citations.
'''

from hashlib import md5
from pathlib import Path
from zipfile import ZipFile
import os
import pandas as pd


def get_md5(x):
    return md5(x.lower().encode("utf-8")).hexdigest()


script_name = Path(__file__).stem
path_zip = 'C:/Users/Hannah.Kotula/OneDrive - Motu Economic and Public Policy Research Trust/Desktop/ml_data/from_emma/oa_data_v1_classified.zip'
path_output = f'R:/Personal/Hannah/research_projects/ml/from_py/{script_name}'
os.makedirs(path_output, exist_ok=True)

biblio_labels = ['PREPRINT/WORKING_PAPER/TECHNICAL_REPORT', 'CONFERENCE_PROCEEDINGS', 'BOOK', 'JOURNAL_ARTICLE', 'THESIS']

with ZipFile(path_zip, 'r') as zf:
    for file in zf.namelist():

        if not file.endswith('.tsv'):
            continue
        if 'checkpoints' in file:
            continue

        stem = os.path.basename(file).split('.')[0]

        with zf.open(file) as f:

            df = pd.read_csv(f, sep='\t', header=0)
            df = df.loc[df['label'].isin(biblio_labels)]

            # Format citations (so md5_id is the same as other data).
            df['oa_citation'] = df['oa_citation'].str.replace(r'\n$', '', regex=True)
            df['oa_citation'] = df['oa_citation'].str.strip()
            df['oa_citation'] = df['oa_citation'].str.replace(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', regex=True)  # control characters.

            df['md5_id'] = df['oa_citation'].apply(get_md5)
            df = df.drop(columns=['oa_citation'])

            df.to_csv(os.path.join(path_output, f'{stem}.csv'), encoding='utf-8', index=False)

print("end")
