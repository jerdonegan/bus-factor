# imports
import os
import sys
import argparse

import git
from git import Repo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

def main():
    args = get_args()

    git_name = [git for git in args.git_url.split("/") if git != ''][-1]
    path = os.path.join(os.getcwd(), git_name)

    repo = get_repo(path, args.git_url)

    files = repo.git.execute('git ls-tree --full-tree -r --name-only HEAD').split('\n')

    authors = get_authors_contribution(files, repo)

    authors_df = create_dataframe(authors)

    critical_threshold = .5
    critical_contributions = get_bus_factor(authors_df, critical_threshold)

    print(f'There are {len(critical_contributions)} critical contributiors.')
    print(critical_contributions[['name', 'line_count']])

    if args.save_plots:
        plot_busfactor(authors_df,
                       critical_contributions,
                       critical_threshold,
                       git_name)
        plot_critical_contributors(critical_contributions, git_name)

    if args.to_json:
        authors_df.to_json(f'{git_name}_authors.json')
        critical_contributions.to_json(f'{git_name}_critical.json')
        print(f'Files Saved to {os.getcwd()}\{git_name}_critical.json')

    if args.to_csv:
        authors_df.to_csv(f'{git_name}_authors.csv')
        critical_contributions.to_csv(f'{git_name}_critical.csv')
        print(f'Files Saved to {os.getcwd()}\{git_name}_critical.csv')


def get_args():
    parser = argparse.ArgumentParser()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument('-g', '--git_url',
                        help='Url for Git Repo',
                        action='store',
                        required=True)

    optional.add_argument('-s','--save_plots',
                        help="Save Plots",
                        action='store_true')

    optional.add_argument('-j','--to_json',
                        help="Output data to json",
                        action='store_true')

    optional.add_argument('-c','--to_csv',
                        help="Output data to CSV",
                        action='store_true')

    return parser.parse_args()

def get_repo(path, git_url):
    """
    Takes the url of a github repo and clones it
    Returns a gitpython repo
    """
    try:
        repo = Repo(path)
        print(f'Repo in {path}')
        repo.git.checkout('HEAD', force=True)
    except git.exc.NoSuchPathError:
        sys.exit('Repo does not exist')
    except:
        repo = Repo.clone_from(git_url, path, branch='master')
        print(f'Repo Cloned to {path}')

    return repo

def get_authors_contribution(files, repo):
    """
    Loops through all files and extracts author and number of lines
    Returns a list of tuples
    """
    count_lines = lambda lines: len([l for l in lines if l.strip() != ''])

    authors = []
    for file in files:
        authors.extend(
            [(commit.author.name, count_lines(lines)) for commit, lines in repo.blame('HEAD', file)]
        )
    return authors

def create_dataframe(authors):
    """
    Converts list of tuples into dataframe
    Expands data in dataframe
    """
    # Convert to dataframe
    authors_long_df = pd.DataFrame(authors, columns=['name', 'lines'])

    # Group data by author
    authors_df = authors_long_df.groupby('name').sum()

    # Make Author name a column in dataframe
    authors_df.reset_index(level=0, inplace=True)

    # rename columns
    authors_df.columns = ['name', 'line_count']

    # Sort by line count
    authors_df = authors_df.sort_values('line_count', ascending=False)

    # Add new columns to dataframe
    authors_df['total_line_count'] = authors_df.line_count.cumsum()
    authors_df['total_author_count'] = list(range(1, authors_df.shape[0]+1))
    authors_df['total_line_percent'] = authors_df.total_line_count/authors_df.total_line_count.max()
    authors_df['line_percent'] = authors_df.line_count/authors_df.line_count.sum()

    return authors_df.reset_index(drop=True)

def get_bus_factor(authors_df, critical_threshold):
    return authors_df[authors_df.total_line_percent < critical_threshold]

def plot_busfactor(authors_df, critical_contributions,
                   critical_threshold, git_name):
    """
    Creates a plot of the Bus Factor
    """
    ct_label = f'{critical_threshold*100:.0f}% Critical Threshold'
    cc = critical_contributions.shape[0]
    title = git_name.replace('_', ' ').replace('-', ' ').title()

    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(12,8))

    authors_df.plot('total_author_count', 'total_line_percent',
                    ax=ax, label='Total Line Percentage')

    plt.xlabel('Number of Authors')
    plt.ylabel('Total Line Percent')
    plt.title(title)

    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax.yaxis.grid(True)

    xlim = authors_df.total_author_count.max()*.05
    ax.set_xlim(-xlim, authors_df.total_author_count.max()+xlim)
    ax.set_ylim(0,1.05)

    ticks =list(np.arange(0,1.01,0.1).round(1))
    ax.set_yticks(ticks)

    ax.axhline(critical_threshold, color='red', linestyle='--', label=ct_label)
    ax.plot([cc], [critical_threshold], 'o', color='red')
    ax.annotate(
        cc,
        xy = [cc, critical_threshold],
        xytext = [cc, critical_threshold+.01],
        color='red',
        size=15,
        horizontalalignment='right',
        verticalalignment='bottom',
    )
    ax.legend()

    filename = f'{git_name}_bus_factor.png'
    fig.savefig(filename)
    print(f'Bus factor Plot saved as: {os.getcwd()}\{filename}')

def plot_critical_contributors(critical_contributions, git_name):
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(12,8))

    cc = critical_contributions.shape[0]
    title = git_name.replace('_', ' ').replace('-', ' ').title()
    title = f'{title} - Top {cc} contributers'

    critical_contributions.plot.bar(
        'name', 'line_percent',
        ax=ax, label='Line Percentage per Author',
        color='orange'
    )
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax.yaxis.grid(True)

    plt.xticks(rotation=30)
    plt.xlabel('Author')
    plt.ylabel('Total Percent')
    plt.title(title)
    plt.tight_layout()

    filename = f'{git_name}_critical_contributors.png'
    fig.savefig(filename)
    print(f'Critical Contributors Plot saved as: {os.getcwd()}\{filename}')

if __name__ == '__main__':
    main()
