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

subject = subjects[0]

difference_total_list = [] #array for time-frequency data for each subject induced. Dim: 40x (TF-Dim)
difference_induced_list = []
difference_evoked_list = []
null_condition_list = []

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

for subject in subjects:
    epochs = mne.read_epochs(fname.epochs(subject=subject))
    #epochs.equalize_event_counts(["cond1", "cond2"])
    epochs.resample(100, npad='auto')
    epochs_induced_cond1 = epochs["cond1"].copy().subtract_evoked()
    epochs_induced_cond2 = epochs["cond2"].copy().subtract_evoked()
    
    #define wavelet parameters --> Go for tradeoff between frequencies and cycles
    freq = np.logspace(*np.log10([5, 50]), num=25)
    cycles = freq / 2. # freq / 10. to be time wise more precise

    #### generate power spectrum with morlet wavelets ####

    #-----total power for given subject -----
    power_cond1= mne.time_frequency.tfr_morlet(epochs["cond1"], freqs=freq, n_cycles=cycles, use_fft=True,
                            return_itc=False, decim=3, n_jobs=n_jobs, picks=config["pick"], average=True)
    
    power_cond2= mne.time_frequency.tfr_morlet(epochs["cond2"], freqs=freq, n_cycles=cycles, use_fft=True,
                        return_itc=False, decim=3, n_jobs=n_jobs, picks=config["pick"], average=True)

    #-----induced power for given subject -----
    power_induced_cond1= mne.time_frequency.tfr_morlet(epochs_induced_cond1, freqs=freq, n_cycles=cycles, use_fft=True,
                            return_itc=False, decim=3, n_jobs=n_jobs, picks=config["pick"], average=True)

    power_induced_cond2= mne.time_frequency.tfr_morlet(epochs_induced_cond2, freqs=freq, n_cycles=cycles, use_fft=True,
                            return_itc=False, decim=3, n_jobs=n_jobs, picks=config["pick"], average=True)

    #-----evoked power for given subject -----
    power_evoked_cond1 = mne.combine_evoked([power_cond1, power_induced_cond1],weights=[1,-1])
    power_evoked_cond2 = mne.combine_evoked([power_cond2, power_induced_cond2],weights=[1,-1])

    #-----difference between conditions power for given subject -----
    difference_total = mne.combine_evoked([power_cond1,power_cond2],weights=[1,-1])
    difference_evoked = mne.combine_evoked([power_evoked_cond1,power_evoked_cond2],weights=[1,-1])
    difference_induced = mne.combine_evoked([power_induced_cond1,power_induced_cond2],weights=[1,-1])

    difference_total_list.append(difference_total)
    difference_evoked_list.append(difference_evoked)
    difference_induced_list.append(difference_induced)
    #t-test null condition list
    null_condition_list.append(np.squeeze(np.zeros(shape=difference_induced.data[0].shape)))


    # #### Plot section ####
    fig_sub, ax_sub = subplotTF(difference_total,difference_evoked,difference_induced)
    addFigure(subject, fig_sub, "Total / Evoked / Induced  power (left-to-right)", "Time-Frequency")

    fig_1, ax_1 = subplotTF(power_cond1,power_induced_cond1,power_evoked_cond1)
    addFigure(subject, fig_1, "Condition FACES: Total / Evoked / Induced (left-to-right)", "Time-Frequency")

    fig_2, ax_2 = subplotTF(power_cond2,power_induced_cond2,power_evoked_cond2)
    addFigure(subject, fig_2, "Condition CARS: Total / Evoked / Induced (left-to-right)", "Time-Frequency")

    #plot power spectrum
    fig_psd = epochs.plot_psd(fmin=2., fmax=50., average=True, spatial_colors=False, show=False)
    addFigure(subject, fig_psd, "Power spectrum of epochs", "Time-Frequency")

    #power_total.plot_topo(show=False)

difference_total_average = mne.combine_evoked(difference_total_list, weights="equal")
difference_evoked_average = mne.combine_evoked(difference_evoked_list, weights="equal")
difference_induced_average = mne.combine_evoked(difference_induced_list, weights="equal")

fig_across_sub, ax_across_sub = subplotTF(difference_total_average,difference_evoked_average,difference_induced_average)
addFigure(None, fig_across_sub, "Subject average Total / Evoked / Induced  power (left-to-right)", "Time-Frequency", totalReport=True)


difference_induced_stacked = np.stack([difference_induced.data[0] for difference_induced in difference_induced_list])
stacked_zeros = np.stack(null_condition_list)


############# plot permutation t test on average #################################
t_values, clusters, cluster_p_values, h0 = mne.stats.permutation_cluster_test([difference_induced_stacked, stacked_zeros], threshold=2)
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