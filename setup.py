import cx_Freeze
import os.path

executables = [cx_Freeze.Executable("C:\\Users\\Freek\\Documents\\Elite 2Deep Space\\Elite2Deep.py")]

localdir = "C:\\Users\\Freek\\Documents\\Elite 2Deep Space\\"

cx_Freeze.setup(
    name="El33t 2D",
    options={
        "build_exe": {"packages":["pygame","numpy"],#, "render", "config", "assets"],
            "includes":["render", "config", "assets"],
            "include_files":[
                localdir+"spaceship.py",
                localdir+"utils.py",
                localdir+"mainmenu.py",
                localdir+"weapons.py",
                #localdir+"font",
                localdir+"mkl_intel_thread.dll",
                #localdir+"render",
                #localdir+"config",
                #localdir+"assets"
            ]
        }
    },
    executables = executables,
    version="0.9.0"
)
