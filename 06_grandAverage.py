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
peak_list = []

for subject in subjects:
    try:
        # evoked_rare_list.append(mne.Evoked(fname.evokedRare(subject=subject)))
        # evoked_frequent_list.append(mne.Evoked(fname.evokedFrequent(subject=subject)))
        # evoked_rare_list.append(mne.io.read_raw_fif(fname.evokedRare(subject=subject)))
        # evoked_rare_list.append(mne.io.read_raw_fif(fname.evokedRare(subject=subject)))
        epoch = mne.read_epochs(fname.epochs(subject=subject))
        evoked_rare_list.append(epoch["rare"].average())
        evoked_frequent_list.append(epoch["frequent"].average())

        #get peaks
        _,_,peak_rare = epoch["rare"].average().pick(config["pick"]).get_peak(return_amplitude=True)
        _,_,peak_frequent = epoch["frequent"].average().pick(config["pick"]).get_peak(return_amplitude=True)
        peak_list.append([peak_rare, peak_frequent])

    except FileNotFoundError:
        print("Please run step 05 for all subject before computing the grand average")

rareAverage = mne.grand_average(evoked_rare_list)
frequentAverage = mne.grand_average(evoked_frequent_list)
difference_wave = mne.combine_evoked([rareAverage,
                                  frequentAverage],
                                 weights=[1, -1])

average = {"rare": rareAverage, "frequent": frequentAverage, "difference": difference_wave}

fig_evokeds = mne.viz.plot_compare_evokeds(average, picks=config["pick"], show=False)


###t-test
data = np.stack(peak_list)
hist = plt.hist(data, bins=10)
t_values, clusters, cluster_p_values, h0 = mne.stats.permutation_cluster_1samp_test(data)
print("End")