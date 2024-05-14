'''
This code puts each file into a separate folder (folder name is the same as the filename)

We do this because when we run grobid it helps to have each file in a separate folder.
-Grobid processes all files in a folder (and if one file in this folder returns an error, the entire folder won't be processed).
'''

from pathlib import Path
import glob
import os
import shutil

script_name = Path(__file__).stem
source_folder = "R:/Personal/Hannah/research_projects/ml/from_py/oa_data_v3"
output_folder = f"R:/Personal/Hannah/research_projects/ml/from_py/{script_name}"
os.makedirs(output_folder, exist_ok=True)

filepaths = glob.glob(os.path.join(source_folder, "*.txt"))
for i, filepath in enumerate(filepaths):

    filename = os.path.basename(filepath).split('.')[0]
    new_path = os.path.join(output_folder, filename)
    os.makedirs(new_path, exist_ok=True)
    shutil.copy2(filepath, new_path)

print("end")
