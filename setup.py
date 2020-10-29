# coding: utf-8
# Copyright (c) 2019-2020 Latona. All rights reserved.
# import os
# import sys
from setuptools import setup, find_packages
# import subprocess

# CMD_AMD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aion/mysql/install_amd.sh')
# cpu = "amd"

# if '--cpu' in sys.argv:
#     index = sys.argv.index('--cpu')
#     sys.argv.pop(index)
#     cpu = sys.argv.pop(index)
# if cpu == "amd":
#     if os.path.exists(CMD_AMD):
#         subprocess.check_call(CMD_AMD, shell=True)

setup(
    name="aion",
    version="0.0.1",
    author="sho ishii",
    author_email="sho.i@latonaio",
    packages=find_packages(),
    install_requires=[
        "python-dateutil",
        "protobuf>=3.11.3",
        "grpcio",
        "mysqlclient",
        "pymongo",
        "retry",
    ],
)
