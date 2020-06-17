from cx_Freeze import *
import pathlib
import os
blenderClient = pathlib.Path(__file__).resolve().parent/ 'Blender_Clients/blender_for_RMIT/'
print(str(blenderClient))
# Dependencies are automatically detected, but it might need
# fine tuning.
# When using flask-sqlalchemy add sqlite3.dll to include_files
buildOptions = dict(
    packages = ["os", "sys", "ctypes", "Utils"],
    bin_path_excludes = [str(blenderClient)],
    include_files = ['ITACL-Patch-Final.png','RMIT_BlenderDriver.py',str(blenderClient), "ITACL-Patch-Final.ico", str(blenderClient) + r'\2.81\python\lib\site-packages\win32'],
    include_msvcr = True,
    excludes = [str(blenderClient)],
)

# http://msdn.microsoft.com/en-us/library/windows/desktop/aa371847(v=vs.85).aspx
shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "RMIT",                   # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]RMITGUIProcess.exe",    # Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,  # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
    ]

msi_data = {"Shortcut": shortcut_table}  # This will be part of the 'data' option of bdist_msi
path = R"C:\Program Files\RMIT"
bdistOptions = dict(
    upgrade_code =  "{96a85bac-52af-4019-9e94-3afcc9e1ad0c}",
    add_to_path = False,
    install_icon="ITACL-Patch-Final.ico",
    target_name="RMIT",
    data = msi_data,
)

'''
cx_Freeze works on Windows, Mac and Linux, but on each platform it only makes an executable
that runs on that platform. So if you want to freeze your program for Windows, freeze it on 
Windows; if you want to run it on Macs, freeze it on a Mac.

sys.platform values:
┍━━━━━━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━┑
│ System              │ Value               │
┝━━━━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━┥
│ Linux               │ linux or linux2 (*) │
│ Windows             │ win32               │
│ Windows/Cygwin      │ cygwin              │
│ Windows/MSYS2       │ msys                │
│ Mac OS X            │ darwin              │
│ OS/2                │ os2                 │
│ OS/2 EMX            │ os2emx              │
│ RiscOS              │ riscos              │
│ AtheOS              │ atheos              │
│ FreeBSD 7           │ freebsd7            │
│ FreeBSD 8           │ freebsd8            │
│ FreeBSD N           │ freebsdN            │
│ OpenBSD 6           │ openbsd6            │
┕━━━━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━┙
(*) Prior to Python 3.3, the value for any Linux version is always linux2; after, it is linux.
https://stackoverflow.com/questions/446209/possible-values-from-sys-platform
'''

import sys
base = None
#if (sys.platform == "win32"): # GUI applications require a different base on Windows (the default is for a console application).
#     base = "Win32GUI"

executables = [
    Executable(
    'RMITGUIProcess.py',
    base=base,
    icon = "ITACL-Patch-Final.ico",
    copyright="Copyright (C) 2020 NASA IT-C1",)
]

setup(name='RMIT',
      version = '1.0',
      description = 'Rapid Model Import Tool',
      options = dict(build_exe = buildOptions, bdist_msi = bdistOptions),
      executables = executables)