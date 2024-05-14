'''
This code runs grobid (with consolidation on) for unmatched citations.

Grobid uses crossref to consoldiate citations.

Before running this script
-Open docker
-Run following line in command line
    docker run -t --rm --init -p 8070:8070 -v "C:\\Users\\Hannah.Kotula\\grobid_modified6.yaml:/opt/grobid/grobid-home/config/grobid.yaml:ro" lfoppiano/grobid:0.7.3
-(Note: if I run grobid by clicking run in docker, this script doesn't work.)
'''

from grobid_client.grobid_client import GrobidClient
from pathlib import Path
import glob
import os
import pandas as pd

pd.options.display.max_colwidth = 1000
script_name = Path(__file__).stem

path_base = 'R:/Personal/Hannah/research_projects/ml'
config_file = os.path.join(path_base, 'code_other/config.json')
path_csv = os.path.join(path_base, f'from_openalex/run_openalex01/for_crossref')

path_txt = os.path.join(path_base, f'from_py/{script_name}/txt_files_for_grobid')
path_xml = os.path.join(path_base, f'from_py/{script_name}/xml_files_from_grobid')
os.makedirs(path_txt, exist_ok=True)
os.makedirs(path_xml, exist_ok=True)

# CSV TO TXT & PUT IN INDIVIDUAL FOLDER

csv_filepaths = glob.glob(f'{path_csv}/metadata_*.csv', recursive=False)
for csv_filepath in csv_filepaths:

    try:
        df_i = pd.read_csv(csv_filepath)
    except pd.errors.EmptyDataError:
        print("Empty csv file")
        continue

    df_i = df_i.rename(columns={'0': 'raw_citation'})

    stem = os.path.basename(csv_filepath).split('.')[0]
    path_txt_i = os.path.join(path_txt, stem)
    os.makedirs(path_txt_i, exist_ok=True)

    df_i['raw_citation'] = df_i['raw_citation'].str.strip()
    df_i['raw_citation'].to_csv(f'{path_txt_i}/{stem}.txt', header=False, index=False, encoding="utf-8")

# RUN GROBID ON EACH FOLDER

path_input_list = [f.path for f in os.scandir(path_txt) if f.is_dir()]
client = GrobidClient(config_path=config_file)

for i, path_input_i in enumerate(path_input_list):
    client.process('processCitationList', path_input_i, consolidate_citations=True, output=path_xml, include_raw_citations=True)

print("end")
