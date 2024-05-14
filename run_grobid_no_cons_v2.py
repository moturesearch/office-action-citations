'''
This code runs grobid on OA citations (without consolidating them).

Before running this script
-Open docker
-Run following line in command line
    docker run -t --rm --init -p 8070:8070 -v "C:\\Users\\Hannah.Kotula\\grobid_modified6.yaml:/opt/grobid/grobid-home/config/grobid.yaml:ro" lfoppiano/grobid:0.7.3
-(Note: if I run grobid by clicking run in docker, this script doesn't work.)
'''

from grobid_client.grobid_client import GrobidClient
import os

version = 'v2'
path_base = 'R:/Personal/Hannah/research_projects/ml'
config_file = os.path.join(path_base, 'code_other/config.json')
path_txt = os.path.join(path_base, 'from_py/file1folder1_v2')

path_output_grobid = os.path.join(path_base, f'from_py/grobid_output_{version}')
os.makedirs(path_output_grobid, exist_ok=True)

# GROBID
client = GrobidClient(config_path=config_file)
path_input_list = [f.path for f in os.scandir(path_txt) if f.is_dir()]

for i, path_input in enumerate(path_input_list):
    client.process('processCitationList', path_input, consolidate_citations=False, output=path_output_grobid, include_raw_citations=True)

print("end")
