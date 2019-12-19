# PyEdna

A strain analysis tool written in Python


## Getting Started

### Using Git and Github

Github is a tool for sharing version-controlled software. You don't _have_ to use GitHub to use this software, but I recommend that you do, to make sure that you can easily get the latest version.

To do so, [**create an account on GitHub**](https://github.com/join) if you don't already have one.

You can use [Git](https://git-scm.com/) to keep your copy of PyEdna up to date. Please be sure to visit [Git's website](https://git-scm.com/) and **download & install Git for your operating system**.

### Installing Python

PyEdna is written in Python 3.7. To run PyEdna on your computer, you will need a local installation of Python 3. Please follow the instructions below to install Python via [**Anaconda distribution**](https://anaconda.org) for your respective operating system:

* [macOS](./mac_conda_install.md)
* [Windows](./windows_conda_install.md)

### Installing PyEdna

#### With Git

If you have installed git, you can install PyEdna with a single command. In a terminal (e.g. Anaconda Prompt), give the command `pip install git+https://github.com/simon-ball/PyEdna`

You can also clone the repository locally, either using git, or using [Github's desktop application ](https://desktop.github.com/)

#### Without Git

Use the "Clone or Download" button on the right hand side of the screen to download a copy of PyEdna's code. Extract it to a file on your computer. To simplify importing the library, add this location to the [Python Path variable ](https://stackoverflow.com/questions/3402168/).


## Running PyEdna

You can start PyEdna by importing the Python library and calling its `start()` method

    >>> import pyedna
    >>> pyedna.start()

You can also use the analysis tools directly, without the GUI, using the class `pyedna.EdnaCalc`

## Issues?

Please submit issues to the [project's issue tracker](https://github.com/simon-ball/PyEdna/issues) on Github. 