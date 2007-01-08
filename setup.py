# setup.py
from distutils.core import setup
import py2exe

setup(windows=["GDBManager.py"],
        data_files=[
            (".",[
                "default.png"]),
            ("docs",[
                "docs/README.txt"])
        ]
)
