# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
# author: adefossez and adiyoss

import json
import logging
import os
import random
import re
import shutil

from .audio import Audioset

logger = logging.getLogger(__name__)


def match_dns(noisy, clean):
    """match_dns.
    Match noisy and clean DNS dataset filenames.

    :param noisy: list of the noisy filenames
    :param clean: list of the clean filenames
    """
    logger.debug("Matching noisy and clean for dns dataset")
    noisydict = {}
    extra_noisy = []
    for path, size in noisy:
        match = re.search(r'fileid_(\d+)\.wav$', path)
        if match is None:
            # maybe we are mixing some other dataset in
            extra_noisy.append((path, size))
        else:
            noisydict[match.group(1)] = (path, size)
    noisy[:] = []
    extra_clean = []
    copied = list(clean)
    clean[:] = []
    for path, size in copied:
        match = re.search(r'fileid_(\d+)\.wav$', path)
        if match is None:
            extra_clean.append((path, size))
        else:
            noisy.append(noisydict[match.group(1)])
            clean.append((path, size))
    extra_noisy.sort()
    extra_clean.sort()
    clean += extra_clean
    noisy += extra_noisy


def match_files(noisy, clean, matching="sort"):
    """match_files.
    Sort files to match noisy and clean filenames.
    :param noisy: list of the noisy filenames
    :param clean: list of the clean filenames
    :param matching: the matching function, at this point only sort is supported
    """
    if matching == "dns":
        # dns dataset filenames don't match when sorted, we have to manually match them
        match_dns(noisy, clean)
    elif matching == "sort":
        noisy.sort()
        clean.sort()
    else:
        raise ValueError(f"Invalid value for matching {matching}")


class NoisyCleanSet:
    def __init__(self, json_dir, matching="sort", length=None, stride=None,
                 pad=True, sample_rate=None):
        """__init__.

        :param json_dir: directory containing both clean.json and noisy.json
        :param matching: matching function for the files
        :param length: maximum sequence length
        :param stride: the stride used for splitting audio sequences
        :param pad: pad the end of the sequence with zeros
        :param sample_rate: the signals sampling rate
        """
        noisy_json = os.path.join(json_dir, 'noisy.json')
        clean_json = os.path.join(json_dir, 'clean.json')
        with open(noisy_json, 'r') as f:
            noisy = json.load(f)
        with open(clean_json, 'r') as f:
            clean = json.load(f)

        match_files(noisy, clean, matching)
        kw = {'length': length, 'stride': stride, 'pad': pad, 'sample_rate': sample_rate}
        self.clean_set = Audioset(clean, **kw)
        self.noisy_set = Audioset(noisy, **kw)

        assert len(self.clean_set) == len(self.noisy_set)

    def __getitem__(self, index):
        return self.noisy_set[index], self.clean_set[index]

    def __len__(self):
        return len(self.noisy_set)


def split_train_val(clean_dir, noisy_dir, matching="sort", ratio=0.1, seed=42):
    clean_list = os.listdir(clean_dir)
    noisy_list = os.listdir(noisy_dir)

    match_files(noisy_list, clean_list, matching)

    assert len(clean_list) == len(noisy_list)

    random.seed(seed)
    val_list_set = set(random.sample(clean_list, int(ratio*len(clean_list))))
    
    train_clean_dir, val_clean_dir = split_dir(clean_dir)
    train_noisy_dir, val_noisy_dir = split_dir(noisy_dir)

    for file in clean_list:
        if file in val_list_set:
            shutil.copy2(os.path.join(clean_dir, file), val_clean_dir)
            shutil.copy2(os.path.join(noisy_dir, file), val_noisy_dir)
        else:
            shutil.copy2(os.path.join(clean_dir, file), train_clean_dir)
            shutil.copy2(os.path.join(noisy_dir, file), train_noisy_dir)


def split_dir(dir):
    folder = os.path.basename(os.path.normpath(dir))

    train_dir = os.path.join(dir, "..", "train_"+folder)
    os.makedirs(train_dir, exist_ok=True)
    
    val_dir = os.path.join(dir, "..", "val_"+folder)
    os.makedirs(val_dir, exist_ok=True)

    return train_dir, val_dir
