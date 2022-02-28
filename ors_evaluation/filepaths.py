#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

from pathlib import Path
import yaml


class FilePaths:
    """Manages folder structure of output data"""

    def __init__(self, yaml_file: str, out_dir: str):
        """
        Initialize
        :param yaml_file: YAML file containing the paths to the output directories and files
        :param out_dir: Path to the output directory in which the directories should be created
        """
        self.OUT_DIR = Path(out_dir)
        paths = self.read_yaml(yaml_file)
        for k, v in paths.items():
            setattr(self, k, self.OUT_DIR / v)

    def read_yaml(self, yaml_file):
        """
        Read yaml file
        :param yaml_file: YAML file containing the paths to the output directories and files
        :return:
        """
        with open(yaml_file, 'r') as f:
            paths = yaml.load(f, Loader=yaml.FullLoader)
        return paths

    def create_dirs(self):
        """
        Creats sub directories
        :return:
        """
        for var, path in self.__dict__.items():
            if str(var).endswith("_DIR"):
                path.mkdir(parents=False, exist_ok=True)

