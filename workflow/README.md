[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# UsefulGnom/workflows

Implements workflows to test and evaluate **UsefulGnom** using [snakemake](https://snakemake.readthedocs.io/en/stable/).


## Usage

### Base / Total Coverage Depth, Frequncy Matrix, Mutation Statistics

Before running any rules, set the desired **Enrionmental Variables** in `base_coverage.smk`

Static Snakmake Rules can be run by 
```bash
    snakemake -c 1 basecnt_coverage_depth
```
for  1) calculating basecnt coverage depth

```bash
    snakemake -c 1 total_coverage_depth
```
for 2) total coverage depth and 

```bash
    snakemake -c 1 mutation_statistics
```
3) computing frequency matrix+calculating mutations statistics


## Environment

Then, create a new environment for the project:
```commandline
cd UsefulGnom/
mamba env create -f environment.yml
```



Then add in all project specific dependencies via:
```commandline
cd UsefulGnom/
conda activate UsefulGnom
pip install -e .
```
This should install all the dependencies, and make the package available in the environment `UsefulGnom` that is currently active by running the prior command.



