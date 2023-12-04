#!/usr/bin/env python
# Copyright (c) Facebook, Inc. and its affiliates.

import glob
import os
import shutil
from os import path
from setuptools import find_packages, setup
from typing import List

def get_version():
    init_py_path = path.join(path.abspath(path.dirname(__file__)), "detectron2", "__init__.py")
    init_py = open(init_py_path, "r").readlines()
    version_line = [l.strip() for l in init_py if l.startswith("__version__")][0]
    version = version_line.split("=")[-1].strip().strip("'\"")

    # The following is used to build release packages.
    # Users should never use it.
    suffix = os.getenv("D2_VERSION_SUFFIX", "")
    version = version + suffix
    if os.getenv("BUILD_NIGHTLY", "0") == "1":
        from datetime import datetime

        date_str = datetime.today().strftime("%y%m%d")
        version = version + ".dev" + date_str

        new_init_py = [l for l in init_py if not l.startswith("__version__")]
        new_init_py.append('__version__ = "{}"\n'.format(version))
        with open(init_py_path, "w") as f:
            f.write("".join(new_init_py))
    return version


def get_model_zoo_configs() -> List[str]:
    """
    Return a list of configs to include in package for model zoo. Copy over these configs inside
    detectron2/model_zoo.
    """

    # Use absolute paths while symlinking.
    source_configs_dir = path.join(path.dirname(path.realpath(__file__)), "configs")
    destination = path.join(
        path.dirname(path.realpath(__file__)), "detectron2", "model_zoo", "configs"
    )
    # Symlink the config directory inside package to have a cleaner pip install.

    # Remove stale symlink/directory from a previous build.
    if path.exists(source_configs_dir):
        if path.islink(destination):
            os.unlink(destination)
        elif path.isdir(destination):
            shutil.rmtree(destination)

    if not path.exists(destination):
        try:
            os.symlink(source_configs_dir, destination)
        except OSError:
            # Fall back to copying if symlink fails: ex. on Windows.
            shutil.copytree(source_configs_dir, destination)

    config_paths = glob.glob("configs/**/*.yaml", recursive=True)
    return config_paths


# For projects that are relative small and provide features that are very close
# to detectron2's core functionalities, we install them under detectron2.projects
PROJECTS = {
    "detectron2.projects.point_rend": "projects/PointRend/point_rend",
    "detectron2.projects.deeplab": "projects/DeepLab/deeplab",
    "detectron2.projects.panoptic_deeplab": "projects/Panoptic-DeepLab/panoptic_deeplab",
}

setup(
    name="detectron2",
    version=get_version(),
    author="FAIR",
    url="https://github.com/facebookresearch/detectron2",
    description="Detectron2 is FAIR's next-generation research "
    "platform for object detection and segmentation.",
    packages=find_packages(exclude=("configs", "tests*")) + list(PROJECTS.keys()),
    package_dir=PROJECTS,
    package_data={"detectron2.model_zoo": get_model_zoo_configs()},
    python_requires=">=3.6",
    install_requires=[
        # Do not add opencv here. Just like pytorch, user should install
        # opencv themselves, preferrably by OS's package manager, or by
        # choosing the proper pypi package name at https://github.com/skvark/opencv-python
        "termcolor>=1.1",
        "Pillow>=7.1",  # or use pillow-simd for better performance
        "yacs>=0.1.6",
        "tabulate",
        "cloudpickle",
        "matplotlib",
        "tqdm>4.29.0",
        "tensorboard",
        "fvcore>=0.1.3,<0.1.4",  # required like this to make it pip installable
        "iopath>=0.1.2",
        "pycocotools>=2.0.2",  # corresponds to https://github.com/ppwwyyxx/cocoapi
        "future",  # used by caffe2
        "pydot",  # used to save caffe2 SVGs
        "dataclasses; python_version<'3.7'",
        "omegaconf>=2",
    ],
    extras_require={
        "all": [
            "shapely",
            "psutil",
            "hydra-core",
            "panopticapi @ https://github.com/cocodataset/panopticapi/archive/master.zip",
        ],
        "dev": [
            "flake8==3.8.1",
            "isort==4.3.21",
            "black==20.8b1",
            "flake8-bugbear",
            "flake8-comprehensions",
        ],
    },
)
