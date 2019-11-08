# imports
import os
import sys

import git
from git import Repo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

class BusFactor:

    def __init__(self, repo_url, critical_threshold=.5):
        self.repo_url = repo_url
        self._critical_threshold = critical_threshold
        self._create_path()
        self._clone_repo()
        self._get_files()
        self._get_authors()
        self._create_dataframe()
        self._get_critical_contributers()
        self._plot_busfactor()
        self._plot_critical_contributors()


    @property
    def critical_threshold(self):
        """

        """
        return self._critical_threshold


    @critical_threshold.setter
    def critical_threshold(self, ct):
        """

        """
        self._critical_threshold = ct
        self._get_critical_contributers()
        self._plot_busfactor()
        self._plot_critical_contributors()


    def _create_path(self):
        """

        """
        path = os.path.expanduser(f'~/')
        self.git_name = self.repo_url.rsplit('/',1)[1]
        self.path = os.path.join(path, self.git_name)
        if not os.path.exists(self.path):
            os.mkdir(self.path)


    def _clone_repo(self):
        """

        """
        try:
            self.repo = Repo(self.path)
            print(f'Repo is in {self.path}')
            self.repo.git.checkout('HEAD', force=True)
        except:# [git.exc.NoSuchPathError, git.exc.InvalidGitRepositoryError]:
            self.repo = Repo.clone_from(self.repo_url, self.path, branch='master')
            print(f'Repo Cloned to {self.path}')

    def _get_files(self):
        """

        """
        self._files = self.repo.git.execute(
            'git ls-tree --full-tree -r --name-only HEAD'
            ).split('\n')


    def _get_authors(self):
        """

        """
        def count_lines(lines):
            used_lines = [l for l in lines if l.strip() != '']
            return len(used_lines)

        self.authors = {}
        for file in self._files:
            for commit, lines in self.repo.blame('HEAD', file):
                if commit.author.name in self.authors.keys():
                    self.authors[commit.author.name] += count_lines(lines)
                else:
                    self.authors[commit.author.name] = count_lines(lines)


    def _create_dataframe(self):
        """

        """
        df = pd.DataFrame.from_dict(
            self.authors,
            orient='index'
            ).reset_index()
        df.columns = ['author', 'lines']
        # df = df.groupby('author').sum()
        df = df.reset_index().sort_values(
            'lines',
            ascending=False
            )

        df['total_line_count'] = df.lines.cumsum()
        df['author_count'] = list(range(1, len(df)+1))
        df['total_line_percent'] = df.total_line_count/df.lines.sum()
        df['line_percent'] = df.lines/df.lines.sum()

        self.authors_df = df.reset_index().drop('index', axis=1)


    def _get_critical_contributers(self):
        """

        """
        self.critical_contributers_df = self.authors_df[
            self.authors_df.total_line_percent < self._critical_threshold
        ]
        if self.critical_contributers_df.empty:
            self.critical_contributers_df = pd.DataFrame(
                self.authors_df.iloc[0, :]
                ).T


    def _get_path(self, path):
        """

        """
        if path:
            file_path = path
        else:
            file_path = os.getcwd()

        return file_path


    def _plot_busfactor(self, path=None):
        """

        """
        ct_label = f'{self.critical_threshold*100:.0f}% Critical Threshold'
        cc = self.critical_contributers_df.shape[0]
        title = self.git_name.replace('-', ' ').title()

        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(12,8))

        self.authors_df.plot('author_count', 'total_line_percent',
                            ax=ax, label='Total Line Percentage')

        plt.xlabel('Number of Authors')
        plt.ylabel('Total Line Percent')
        plt.title(title)

        ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
        ax.yaxis.grid(True)

        xlim = self.authors_df.author_count.max()*.05
        ax.set_xlim(-xlim, self.authors_df.author_count.max()+xlim)
        ax.set_ylim(0,1.05)

        ticks =list(np.arange(0,1.01,0.1).round(1))
        ax.set_yticks(ticks)

        ax.axhline(self.critical_threshold, color='red', linestyle='--', label=ct_label)
        ax.plot([cc], [self.critical_threshold], 'o', color='red')
        ax.annotate(
            cc,
            xy = [cc, self.critical_threshold],
            xytext = [cc, self.critical_threshold+.01],
            color='red',
            size=15,
            horizontalalignment='right',
            verticalalignment='bottom',
        )
        ax.legend()
        self.bus_factor_plot = fig
        plt.close()

    def save_bus_factor_plot(self, path=None):
        """

        """
        file_path = self._get_path(path)
        gn = self.git_name.replace('-', '_')
        fp = f'{file_path}/bus_factor_{gn}.png'
        self.bus_factor_plot.savefig(fp)
        return f'Bus Factor Plot saved as: {fp}'

    def _plot_critical_contributors(self, path=None):
        """
        """
        cc = self.critical_contributers_df.shape[0]
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(12,8))

        title = self.git_name.replace('-', ' ').title()
        title = f'{title} - Top {cc} contributers'

        self.critical_contributers_df.plot.bar(
            'author', 'line_percent',
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

        self.critical_contributers_fig = fig
        plt.close()

    def save_critical_plot(self, path=None):
        """

        """
        file_path = self._get_path(path)
        gn = self.git_name.replace('-', '_')
        fp = f'{file_path}/critical_contributers_{gn}.png'
        self.critical_contributers_fig.savefig(fp)

        return f'Critical Contributers Plot saved as: {fp}'
