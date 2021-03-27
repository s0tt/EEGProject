import argparse
import mne
import ccs_eeg_utils
from config import config, fname, n_jobs
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
from utils import handleSubjectArg, readRawFif, addFigure
import json, os
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('subjects',metavar='subs', nargs='+',help='Subject list')
args = parser.parse_args()
subjects = args.subjects

evoked_rare_list = []
evoked_frequent_list = []

for subject in subjects:
    try:
        # evoked_rare_list.append(mne.Evoked(fname.evokedRare(subject=subject)))
        # evoked_frequent_list.append(mne.Evoked(fname.evokedFrequent(subject=subject)))
        # evoked_rare_list.append(mne.io.read_raw_fif(fname.evokedRare(subject=subject)))
        # evoked_rare_list.append(mne.io.read_raw_fif(fname.evokedRare(subject=subject)))
        epoch = mne.read_epochs(fname.epochs(subject=subject))
        evoked_rare_list.append(epoch["rare"].average())
        evoked_frequent_list.append(epoch["frequent"].average())

    except FileNotFoundError:
        print("Please run step 05 for all subject before computing the grand average")

rareAverage = mne.grand_average(evoked_rare_list)
frequentAverage = mne.grand_average(evoked_frequent_list)
difference_wave = mne.combine_evoked([rareAverage,
                                  frequentAverage],
                                 weights=[1, -1])

average = {"rare": rareAverage, "frequent": frequentAverage, "diference": difference_wave}

fig_evokeds = mne.viz.plot_compare_evokeds(average, picks="Pz", show=True)


