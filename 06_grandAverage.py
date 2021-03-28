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
        epoch = mne.read_epochs(fname.epochs(subject=subject))
        evoked_rare_list.append(epoch["rare"].average())
        evoked_frequent_list.append(epoch["frequent"].average())

        #get peaks
        difference_wave = mne.combine_evoked([epoch["rare"].average(),epoch["frequent"].average()],weights=[1, -1])
        _,peak_latency,peak_frequent = difference_wave.pick(config["pick"]).crop(tmin=0.35, tmax= 0.6).get_peak(return_amplitude=True)
        peak_list.append([peak_frequent, 0])

    except FileNotFoundError:
        print("Please run step 05 for all subject before computing the grand average")

rare_average = mne.grand_average(evoked_rare_list)
frequent_average = mne.grand_average(evoked_frequent_list)
difference_wave = mne.combine_evoked([rare_average,
                                  frequent_average],
                                 weights=[1, -1])

average = {"rare": rare_average, "frequent": frequent_average, "difference": difference_wave}

fig_evokeds = mne.viz.plot_compare_evokeds(average, picks=config["pick"], show=True)


###t-test
data = np.stack(peak_list)
hist = plt.hist(data, bins=15)
t_values, clusters, cluster_p_values, h0 = mne.stats.permutation_cluster_1samp_test(data)
print("paired permutation cluster t-test p-value:", cluster_p_values)
print("End")