# RMIT Repo

RMIT(Rapid Model Import Tool) is a python executable that processes high fidelity CAD models for use in game engines such as Unity. This repository serves as the code base for this project.

## Prerequisites

There are some requirements in order to properly build this software. This project uses cx_freeze to create the binaries. It also requires Python 3.7.0. This software only works on windows.

    1. Go to Development>RMIT
    2. Install requirements via command line:
        pip install -r requirements.txt
    3.To compile the software via command line: 
        python setup.py build
    4. This will create a build folder with an exe
    (Optional)
    5. If you would like to create a windows installer use this command:
        python setup.py bdist_msi




## Debugging with VSCode & Blender

- Install the extension below in VsCode
- Name: Blender Development
Id: jacqueslucke.blender-development
Description: Tools to simplify Blender development.
Version: 0.0.12
Publisher: Jacques Lucke
VS Marketplace Link: https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development
- With the extension installed, hit F1 in VSCode. Type "Blender Start". 
- Select your blender client. This will create a port between VSCODE and Blender.
- Create breakpoints in VSCode and then hit F1 again. This time select "Blender Run Script" 
- Breakpoints will now trigger during execution flow.
- *NOTE*: You can run add-ons in blender by hitting F3 and searching for your add-on name.
- *NOTE*: You can dynamically load add-ons in VSCode with "Blender Reload Addons"

## Built With

* [Python 3.7](https://www.python.org/downloads/) - Language used
* [Blender 2.8](https://www.blender.org/download/releases/2-80/) - 3D modeling program (*Open Source*)
* [PyQt5](https://pypi.org/project/PyQt5/) - Python GUI Library (Must use version 5.12.2) https://github.com/pyinstaller/pyinstaller/issues/4293

## Contributing

Please see William Little(william.l.little@nasa.gov) or Joseluis Chavez(joseluis.chavez@nasa.gov) for instructions on contributing to this project.

## Versioning

This is a beta release candidate. V1.0

## Authors

* **William Little** (Civil Service)
* **Joseluis Chavez**(Civil Service)
* **Taylor Waddell**(Pathways intern)
* **Arjun Ayyangar**(NIFS intern)
* **Tanya Gupta**(NIFS intern)
* **Ben Fairlamb**(NIFS intern)


