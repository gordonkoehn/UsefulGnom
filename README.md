[![Project Status: WIP – This project is currently under active development.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
[![build](https://github.com/gordonkoehn/UsefulGnom/actions/workflows/test.yml/badge.svg)](https://github.com/gordonkoehn/UsefulGnom/actions/workflows/test.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/charliermarsh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# UsefulGnom

Python package for viral genomic analysis utilities.


## Usage

```python
import usefulgnom as ug
```


### Setting up the repository

To build the package and maintain dependencies, we use [Poetry](https://python-poetry.org/).
In particular, it's good to install it and become familiar with its basic functionalities by reading the documentation. 

To set up the environment (together with development tools), run:
```bash
$ poetry install --with dev
$ poetry run pre-commit install
```

Then, you will be able to run tests:
```bash
$ poetry run pytest
```
... or check the types:
```bash
$ poetry run pyright
```

Alternatively, you may prefer to work with the right Python environment using:
```bash
$ poetry shell
$ pytest
```

### Existing code quality checks
The code quality checks run on GitHub can be seen in ``.github/workflows/test.yml``.

We are using:

  * [Ruff](https://github.com/charliermarsh/ruff) to lint the code.
  * [Black](https://github.com/psf/black) to format the code.
  * [Pyright](https://github.com/microsoft/pyright) to check the types.
  * [Pytest](https://docs.pytest.org/) to run the unit tests.
  * [Interrogate](https://interrogate.readthedocs.io/) to check the documentation.


### Workflow

We use [Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow),
in which modifications of the code should happen via small pull requests.

We recommend submitting small pull requests and starting with drafts outlining proposed changes.



_____


Auguste's scripts for 
 - 1) calculating basecnt coverage depth, 
 - 2) total coverage depth and 
 - 3) computing frequency matrix+calculating mutations statistics