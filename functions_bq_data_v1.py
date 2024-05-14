'''
These functions format data and create text files (for data from BigQuery).
'''

import os
import re


def format_data(df, colname):

    # colname = "npl_biblio"

    df.loc[:, colname] = df.loc[:, colname].astype(str)
    df.loc[:, colname] = df.loc[:, colname].str.title()
    df.loc[:, colname] = df.loc[:, colname].str.replace(r'^\s+|\s+$', '', regex=True)  # removes whitespace from start & end

    to_remove = ['Database Wpi', 'Patent Abstracts', 'Chemical Abstracts', 'Wpi']
    df = df[~df[colname].astype(str).str.startswith(tuple(to_remove))]

    return df


def create_text_files(result, path_output, colname):

    for i, df in enumerate(result.to_dataframe_iterable()):

        df = format_data(df=df, colname=colname)

        sp_char = r'([\u4E00-\u9FFF])|([\u3000-\u303F])|([\u3040-\u309F])|([\u30A0-\u30FF])|([\u0401-\u04f9])'
        df_sp = df[df[colname].str.contains(sp_char)]
        df_no_sp = df[~df[colname].str.contains(sp_char)]

        df_list = [df_sp, df_no_sp]
        sps = ["with_sp", "without_sp"]

        for df_i, sp_j in zip(df_list, sps):

            if df_i.shape[0] == 0:
                continue

            with open(os.path.join(path_output, f"oa_citations_{sp_j}_{i}.txt"), 'w', encoding="utf-8") as f:

                citations = df_i[colname].to_string(header=False, index=False)
                citations = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', citations)  # removes all control characters (eg SOH) except for \n
                citations = re.sub(' +', ' ', citations).strip()

                f.write(citations)
