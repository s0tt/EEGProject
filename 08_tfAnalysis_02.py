import argparse
import mne
import ccs_eeg_utils
from config import config, fname, n_jobs
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
from utils import *
import json, os
import numpy as np

def subplotTF(total, evoked, induced):
    mode = "mean" #"percent"
    baseline = None
    cmax = None
    cmin = None
    fig, ax = plt.subplots(1, 3, constrained_layout=True, figsize=(24, 8))
    ax[0].title.set_text("TF Total difference at {}".format(config["pick"]))
    ax[1].title.set_text("TF Evoked difference at {}".format(config["pick"]))
    ax[2].title.set_text("TF Induced difference at {}".format(config["pick"]))
    total.plot(axes=ax[0],baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False)
    evoked.plot(axes=ax[1], baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False)
    induced.plot(axes=ax[2], baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False)
    return fig, ax

subjects = handleSubjectArg(multiSub=True)

difference_total_list = [] 
difference_induced_list = []
difference_evoked_list = []

for subject in subjects:
    try:
        #array for time-frequency data for each subject induced. Dim: 40x (TF-Dim)
        power_array_subject = readData(fname.tfAnalysis(subject=subject))
        difference_total_list.append(power_array_subject[0]) #total power
        difference_evoked_list.append(power_array_subject[1]) #evoked power
        difference_induced_list.append(power_array_subject[2]) #induced power

    except FileNotFoundError:
        print("Please provide all artefacts from 07_tfAnalysis_01 before running step _02")

difference_total_average = mne.combine_evoked(difference_total_list, weights="equal")
difference_evoked_average = mne.combine_evoked(difference_evoked_list, weights="equal")
difference_induced_average = mne.combine_evoked(difference_induced_list, weights="equal")

fig_across_sub, ax_across_sub = subplotTF(difference_total_average,difference_evoked_average,difference_induced_average)
addFigure(None, fig_across_sub, "Subject average Total / Evoked / Induced  power (left-to-right)", "Time-Frequency", totalReport=True)


difference_induced_stacked = np.stack([difference_induced.data[0] for difference_induced in difference_induced_list])


############# plot permutation t test on average #################################
t_values, clusters, cluster_p_values, h0 = mne.stats.permutation_cluster_test([difference_induced_stacked, 
                                                        np.zeros(shape=difference_induced_stacked.data[0])], threshold=2)


print("#################### Cluster permutation t-test: ###############\n", cluster_p_values)

fig_test, ax_test = plt.subplots(1,3,constrained_layout=True, figsize=(24, 8))
ax_test[0].title.set_text("Across subject induced{}".format(config["pick"]))
ax_test[1].title.set_text("T-Values of cluster permutation test")
ax_test[2].title.set_text("Clusters with significant p-values <= " + str(config["alpha"]))

difference_induced_average.plot(axes= ax_test[0],picks=config["pick"], show=False)
frequencies = np.arange(5, 55, 2)
times = 1e3 * difference_induced_average.times
cluster_array = np.nan * np.ones_like(t_values)

for cluster, p_value in zip(clusters, cluster_p_values):
    if p_value <= config["alpha"]:
        cluster_array[cluster] = difference_induced_average.data[0][cluster]

ax_test[1].imshow(t_values,extent=[times[0], times[-1], frequencies[0], frequencies[-1]],aspect='auto', origin='lower', cmap='gray')
ax_test[2].imshow(cluster_array, extent=[times[0], times[-1], frequencies[0], frequencies[-1]],aspect='auto', origin='lower', cmap='RdBu_r')

addFigure(None, fig_test, "T-test significance over induced average", "Time-Frequency", totalReport=True)
