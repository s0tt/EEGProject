import argparse
import mne
import ccs_eeg_utils
from config import config, fname, n_jobs
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
from utils import *
import json, os
import numpy as np
from scipy.interpolate import interp1d

def subplotTF(total, evoked, induced):
    mode = "mean" #"percent"
    baseline = None if config["tf_baseline"] == "None" else config["tf_baseline"]
    vmax = config["tf_vmax"] * (1e-10)
    vmin = -vmax
    fig, ax = plt.subplots(1, 3, constrained_layout=True, figsize=(24, 8))
    ax[0].title.set_text("TF Total difference at {}".format(config["tf_analyze_pick"]))
    ax[1].title.set_text("TF Evoked difference at {}".format(config["tf_analyze_pick"]))
    ax[2].title.set_text("TF Induced difference at {}".format(config["tf_analyze_pick"]))
    total.plot(axes=ax[0],baseline=baseline,picks=config["tf_analyze_pick"],mode=mode,vmin=vmin,vmax=vmax, show=False)
    evoked.plot(axes=ax[1], baseline=baseline,picks=config["tf_analyze_pick"],mode=mode,vmin=vmin,vmax=vmax, show=False)
    induced.plot(axes=ax[2], baseline=baseline,picks=config["tf_analyze_pick"],mode=mode,vmin=vmin,vmax=vmax, show=False)
    return fig, ax

def plotTopo(power):
    baseline = None if config["tf_baseline"] == "None" else config["tf_baseline"]
    fig = power.plot_topo(baseline=baseline, mode='logratio', title='Average power', show=False)
    return fig

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

fig_across_sub, _ = subplotTF(difference_total_average,difference_evoked_average,difference_induced_average)
fig_topo_evoked = plotTopo(difference_evoked_average)
fig_topo_induced = plotTopo(difference_induced_average)

addFigure(None, fig_topo_evoked, "Evoked: Topology power plot for all computed electrodes", "Time-Frequency", totalReport=True)
addFigure(None, fig_topo_induced, "Induced: Topology power plot for all computed electrodes", "Time-Frequency", totalReport=True)
addFigure(None, fig_across_sub, "Subject average Total / Evoked / Induced  power (left-to-right)", "Time-Frequency", totalReport=True)


difference_induced_stacked = np.stack([difference_induced.data[0] for difference_induced in difference_induced_list])
zero_condition_stacked = np.stack([np.zeros(shape=difference_induced.data[0].shape) for difference_induced in difference_induced_list])

############# plot permutation t test on average #################################
t_values, clusters, cluster_p_values, h0 = mne.stats.permutation_cluster_test([difference_induced_stacked, zero_condition_stacked], threshold=2)


print("#################### Cluster permutation t-test: ###############\n", cluster_p_values)

fig_test, ax_test = plt.subplots(1,3,constrained_layout=True, figsize=(24, 8))
ax_test[0].title.set_text("Across subject induced{}".format(config["tf_analyze_pick"]))
ax_test[1].title.set_text("T-Values of cluster permutation test")
ax_test[2].title.set_text("Clusters with significant p-values <= " + str(config["alpha"]) + ", Color = P-Value")

difference_induced_average.plot(axes= ax_test[0],picks=config["tf_analyze_pick"], show=False)
frequencies = np.arange(5, 55, 2)
times = 1000 * difference_induced_average.times
cluster_array = np.nan * np.ones_like(t_values)

for cluster, p_value in zip(clusters, cluster_p_values):
    if p_value <= config["alpha"]:
        cluster_array[cluster] = p_value

im1 = ax_test[1].imshow(t_values,aspect='auto', origin='lower', cmap='gray')
im2 = ax_test[2].imshow(cluster_array,aspect='auto', origin='lower', cmap='gray')
fig_test.colorbar(im1, ax=ax_test[1])
# linear scaling of log values in 2d array..could not be fixed yet
# ax_test[1].set_yscale("log")
# ax_test[2].set_yscale("log")
# ax_test[1].ylim([5.0,50.0])
fig_test.colorbar(im2, ax=ax_test[2])
ax_test[2].get_yaxis().set_visible(False)
ax_test[2].get_xaxis().set_visible(False)
ax_test[1].get_yaxis().set_visible(False)
ax_test[1].get_xaxis().set_visible(False)

addFigure(None, fig_test, "T-test significance over induced average", "Time-Frequency", totalReport=True)