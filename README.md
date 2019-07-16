# bus-factor
Loads a GitHub repository and outputs who the critical contributers are.

### Required Arguments
* -g, --git Url of the GitHup repository

### Optional Arguments
* -s, --save_plots Outputs two plots:
  * {repo}_critical_contributors.png - Bar plot of the line % for each ccritical contributer
  * {repo}_bus_factor.png - Line plot of the Total Line % vs authors with decreasing line count
* -j, --to_json Outputs data on critical contributers and authors to .json file's
* -c, --to_csv Outputs data on critical contributers and outhors to .csv file's
