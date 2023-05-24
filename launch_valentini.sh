#!/bin/bash
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
# authors: adiyoss and adefossez

python train.py \
  dset=valentini \
  bandmask=0.2 \
  remix=1 \
  shift=8000 \
  shift_same=True \
  stft_loss=True \
  pesq=False \
  eval_every=2 \
  stft_sc_factor=0.1 stft_mag_factor=0.1 \
  epochs=10 \
  batch_size=16 \
  sample_rate=48000 \
  segment=4.5 \
  stride=0.5 \
  ddp=1 $@

