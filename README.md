# Serious Grid World Game (now with zombies!)

BWSI Serious Grid World. A project based approach to learning serious games with AI.

This README will help you get the game running so that you can start your own modifications.

## Prerequisites / Installation

First, you need to have Python on your system. If you think you already have python on your computer, you can double
check with the following: Open either `cmd` (Windows) or Terminal (macOS) and type `python --version`. 
If this throws an error, or shows a version less than Python 3.8, please follow the instructions below to install 
python version 3.8 (the code was tested on 3.8.5).

We are using Anaconda for our python package manager. Anaconda is nice because it comes include with a number of 
packages we will need. While we can provide an Anaconda env file for the project, we've found this actually complicates 
installation. Our plan for installation is to provide pip installation (another python package manager) of the 
packages that we need that are not in Anaconda.

Here are instructions for downloading anaconda. Download the latest version or one that comes with python 3.8 or greater.
Graphical installers [found here](https://www.anaconda.com/products/individual). The Anaconda download includes 
python so downloading Anaconda will get you most of the way there.

The final tool to make sure is set up properly is Git. For a Git primer, 
check out this [help page](https://docs.github.com/en/github/getting-started-with-github/set-up-git)

Once Anaconda, Python, and Git are installed, here are a list of packages that still need to be installed. To install 
these, use pip as follows:
`pip install tensorflow keras keras-rl2 gym>=0.2.3 pygame argparse uuid json xlrd pandas matplotlib`

## Getting Started
Step 0: Install python and the required packages by following the Prerequisites / Installation above.
Step 1: Follow instructions on how to set up an SSH key between your computer and MIT github:
[git help link](https://docs.github.com/en/enterprise-server@2.19/github/authenticating-to-github/connecting-to-github-with-ssh)

Finally: Clone the repository via command prompt:
```
git clone git@github.mit.edu:BWSI-SGAI-2021/SGW_MAIN.git
cd SGW
git status
```

This will get all the repository files on your system. Python files in the main directory can be run to get
an idea of how to use the game.

# Game Details
Out of the box, this is a command line interface (CLI) game and can be ran from a command prompt (or terminal) or 
from an integrated development environment (IDE). The entry points for the code have "RUN" as a prefix.

For example, to run basic tests, use the following command. NOTE: this command prints the help commands
for the CLI options. It will show you the usage and options for the CLI.
```
python RUN_Basic.Tests.py -h
```

More details about the game and this software implementation will be provided over time via lectures.
