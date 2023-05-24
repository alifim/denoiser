#!/bin/bash

noisy_train=dataset/valentini/train_noisy_trainset_28spk_wav
clean_train=dataset/valentini/train_clean_trainset_28spk_wav
noisy_test=dataset/valentini/noisy_testset_wav
clean_test=dataset/valentini/clean_testset_wav
noisy_dev=dataset/valentini/val_noisy_trainset_28spk_wav
clean_dev=dataset/valentini/val_clean_trainset_28spk_wav

mkdir -p egs/valentini/tr
mkdir -p egs/valentini/cv
mkdir -p egs/valentini/tt

python -m denoiser.audio $noisy_train > egs/valentini/tr/noisy.json
python -m denoiser.audio $clean_train > egs/valentini/tr/clean.json

python -m denoiser.audio $noisy_test > egs/valentini/tt/noisy.json
python -m denoiser.audio $clean_test > egs/valentini/tt/clean.json

python -m denoiser.audio $noisy_dev > egs/valentini/cv/noisy.json
python -m denoiser.audio $clean_dev > egs/valentini/cv/clean.json