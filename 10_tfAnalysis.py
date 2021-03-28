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

subjects_tf_list = [] #array for time-frequency data for each subject induced. Dim: 40x (TF-Dim)
null_condition_list = []

subjects_induced_rare_list = []
subjects_induced_frequent_list = []

for subject in subjects:
    epochs = mne.read_epochs(fname.epochs(subject=subject))
    #evoked_difference = mne.combine_evoked([epochs["rare"].average(),epochs["frequent"].average()],weights=[1, -1])
    epochs_induced_rare = epochs["rare"].copy()
    epochs_induced_frequent = epochs["frequent"].copy()
    epochs_induced_rare.subtract_evoked()
    epochs_induced_frequent.subtract_evoked()

    freq = np.logspace(*np.log10([5, 55]), num=25)
    cycles = freq / 2.

    power_induced_rare= mne.time_frequency.tfr_morlet(epochs_induced_rare, freqs=freq, n_cycles=cycles, use_fft=True,
                            return_itc=False, decim=3, n_jobs=6, picks=config["pick"], average=True)

    power_induced_frequent= mne.time_frequency.tfr_morlet(epochs_induced_frequent, freqs=freq, n_cycles=cycles, use_fft=True,
                            return_itc=False, decim=3, n_jobs=6, picks=config["pick"], average=True)

    #plot power spectrum
    fig_psd = epochs.plot_psd(fmin=2., fmax=40., average=True, spatial_colors=False, show=False)
    addFigure(subject, fig_psd, "Power spectrum of epochs", "Time-Frequency")

    # f, ax = plt.subplots()
    # psds, freqs = mne.time_frequency.psd_multitaper(epochs, fmin=2, fmax=40, n_jobs=1, picks=config["pick"])
    # psds = 10. * np.log10(psds)
    # psds_mean = psds.mean(0).mean(0)
    # psds_std = psds.mean(0).std(0)

    # ax.plot(freqs, psds_mean, color='k')
    # ax.fill_between(freqs, psds_mean - psds_std, psds_mean + psds_std,
    #                 color='k', alpha=.5)
    # ax.set(title='Multitaper PSD', xlabel='Frequency (Hz)',
    #     ylabel='Power Spectral Density (dB)')

    # define frequencies to analyse(log-spaced)
    #freqs = [np.logspace(*np.log10([5, 80]), num=25), np.logspace(*np.log10([5, 80]), num=25)]
    #n_cycles = [1, freqs[1] / 2.] #cycles frequency wise

    # for freq, cycles in zip(freqs, n_cycles):
    #     power_total= mne.time_frequency.tfr_morlet(epochs, freqs=freq, n_cycles=cycles, use_fft=True,
    #                             return_itc=False, decim=3, n_jobs=6, picks=config["pick"], average=True)


    subjects_induced_rare_list.append(power_induced_rare)
    subjects_induced_frequent_list.append(power_induced_frequent)


    #power_induced= mne.time_frequency.tfr_morlet(epochs_induced, freqs=freq, n_cycles=cycles, use_fft=True,
    #                        return_itc=False, decim=3, n_jobs=6, picks=config["pick"], average=True)
    
    
    difference_induced = mne.combine_evoked([power_induced_rare,power_induced_frequent],weights=[1,-1])



    subjects_tf_list.append(np.squeeze(difference_induced._data))
    null_condition_list.append(np.squeeze(np.zeros(shape=difference_induced._data.shape)))

    #power_evoked = mne.combine_evoked([power_total,power_induced],weights=[1,-1])
    mode = "percent"
    baseline = None
    cmin = -3
    cmax = 3
    #power_total.plot(baseline=baseline,picks=config["pick"], mode=mode,vmin=cmin,vmax=cmax, show=False, title="TF Total at {}".format(config["pick"]))
    fig_induced = difference_induced.plot(baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False,title="TF Difference Induced at {}".format(config["pick"]))
    addFigure(subject, fig_induced, "Induced power", "Time-Frequency")
        #power_evoked.plot(baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False,title="TF Evoked at {}".format(config["pick"]))

    #power_total.plot_topo(show=False)

induced_rare_average = mne.combine_evoked(subjects_induced_rare_list, weights="equal")
induced_frequent_average = mne.combine_evoked(subjects_induced_frequent_list, weights="equal")


stacked_tf = np.stack(subjects_tf_list)
stacked_zeros = np.stack(null_condition_list)
t_values, clusters, cluster_p_values, h0 = mne.stats.permutation_cluster_test([stacked_tf, stacked_zeros])
print("Cluster permutation t-test:", cluster_p_values)

plt.show()