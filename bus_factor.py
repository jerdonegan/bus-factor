# imports
import os
import sys
import argparse

from bus_class import BusFactor

def main(args):

    bf = BusFactor(args.git)

    critical_contributions = bf.critical_contributers_df
    authors_df = bf.authors_df
    git_name = bf.git_name.replace('-', '_')

    print(f'There are {len(critical_contributions)} critical contributiors.')
    print(critical_contributions[['author', 'lines']])

    if args.save_plots:
        bf.save_critical_plot()
        bf.save_bus_factor_plot()

    if args.to_json:
        git_name = bf.git_name.replace('-', '_')
        authors_df.to_json(f"{git_name}_authors.json")
        critical_contributions.to_json(f'{git_name}_critical.json')
        print(f'Files Saved to {os.getcwd()}')

    if args.to_csv:
        authors_df.to_csv(f'{git_name}_authors.csv')
        critical_contributions.to_csv(f'{git_name}_critical.csv')
        print(f'Files Saved to {os.getcwd()}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument('-g', '--git',
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

    args = parser.parse_args()

    main(args)
