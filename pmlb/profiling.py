import pathlib
import os
import subprocess

import pandas as pd
from pandas_profiling import ProfileReport

from pmlb import fetch_data, dataset_names, get_updated_datasets

def make_profiling(dataset, write_dir, dat_dir='datasets/'):
    print(f'Processing {dataset}')
    df = fetch_data(dataset, local_cache_dir=dat_dir, dropna=False)
    write_path = write_dir.joinpath(dataset + '.html')

    if len(df.columns) > 20:
        df_rand = (
            df
            .drop(columns = ['target'])
            .sample(n=19, axis=1, random_state=42)
        )
        df = pd.concat([df_rand, df.loc[:,['target']]], axis = 1)
        profile = ProfileReport(df, title=dataset, explorative=True)
    else:
        profile = ProfileReport(df, title=dataset, explorative=True)

    profile.to_file(write_path)

def last_commit_message() -> str:
    """
    Get commit message from last commit, excluding merge commits
    """
    command = "git log --no-merges -1 --pretty=%B".split()
    message = subprocess.check_output(command, universal_newlines=True)
    return message

def datasets_to_gen() -> list:
    """
    Return datasets to regenerate profiles for 
    """
    if '[regenerate_profiles]' in last_commit_message():
        print('::set-env name=regenerate_profiles::true')
        return dataset_names
    if 'regenerate_profiles' in os.environ:
        return dataset_names
    updated_sets = get_updated_datasets()
    return updated_sets['changed_datasets']


if __name__ =='__main__':

    # write_dir = 'docs_sources/profile/'
    write_dir = pathlib.Path('docs_sources/profile/')
    write_dir.mkdir(exist_ok=True)

    datasets = datasets_to_gen()

    for dataset in datasets:
        write_path = write_dir.joinpath(dataset + '.html')
        make_profiling(dataset, write_dir)
