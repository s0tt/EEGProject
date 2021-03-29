import argparse
import mne
import ccs_eeg_utils
from config import config, fname, n_jobs
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
from utils import handleSubjectArg, readRawFif, addFigure
import json, os
import numpy as np
import scipy.stats as stats

subjects = handleSubjectArg(multiSub=True)


peak_list = []
evoked_rare_list = []
evoked_frequent_list = []

for subject in subjects:
    try:
        epoch = mne.read_epochs(fname.epochs(subject=subject))
        #epoch.equalize_event_counts(["rare", "frequent"])# TODO: decide if this to keep equalize event counts
        evoked_rare_list.append(epoch["rare"].average())
        evoked_frequent_list.append(epoch["frequent"].average())

        #get peaks
        difference_wave = mne.combine_evoked([epoch["rare"].average(),epoch["frequent"].average()],weights=[1, -1])
        _,peak_latency,peak_amplitude = difference_wave.pick(config["pick"]).crop(tmin=0.30, tmax= 0.6).get_peak(return_amplitude=True)
        peak_list.append(peak_amplitude)

    except FileNotFoundError:
        print("Please run step 05 for all subject before computing the grand average")

rare_average = mne.grand_average(evoked_rare_list)
frequent_average = mne.grand_average(evoked_frequent_list)
difference_wave = mne.combine_evoked([rare_average,
                                  frequent_average],
                                 weights=[1, -1])

average = {"rare": rare_average, "frequent": frequent_average, "difference": difference_wave}

fig_evokeds = mne.viz.plot_compare_evokeds(average, picks=config["pick"], show=True if config["isDialogeMode"] else False)


#RQ: On which ERP-peaks do we find major difference between the conditions
#statistically test with t-test
fig_hist, ax = plt.subplots()
ax.hist(peak_list, bins=15)

t_values, p_value = stats.ttest_1samp(peak_list, 0.0, alternative="greater")


result_str = "T-test: p-value {} {} {} alpha".format(p_value, ">=" if p_value > config["alpha"] else "<", config["alpha"])
print(result_str)
print("Statistically it is {} that the {} ERP is present given this data".format("significant" if p_value < config["alpha"] else "unsignificant", config["task"]))
addFigure(None, fig_evokeds, "Evoked Plot ","Peak-Analysis", totalReport=True, comments=result_str)
addFigure(None, fig_hist, "Peak histogram","Peak-Analysis", totalReport=True)