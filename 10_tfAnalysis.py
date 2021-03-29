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
    epochs.resample(256, npad='auto')
    #evoked_difference = mne.combine_evoked([epochs["rare"].average(),epochs["frequent"].average()],weights=[1, -1])
    epochs_induced_rare = epochs["rare"].copy()
    epochs_induced_frequent = epochs["frequent"].copy()
    epochs_induced_rare.subtract_evoked()
    epochs_induced_frequent.subtract_evoked()
    

    freq = np.logspace(*np.log10([5, 50]), num=25)
    cycles = freq / 2.
    #cycles = 2

    #### generate power spectrum with morlet wavelets ####

    power_rare= mne.time_frequency.tfr_morlet(epochs["rare"], freqs=freq, n_cycles=cycles, use_fft=True,
                            return_itc=False, decim=3, n_jobs=n_jobs, picks=config["pick"], average=True)
    
    power_frequent= mne.time_frequency.tfr_morlet(epochs["frequent"], freqs=freq, n_cycles=cycles, use_fft=True,
                        return_itc=False, decim=3, n_jobs=n_jobs, picks=config["pick"], average=True)

    power_induced_rare= mne.time_frequency.tfr_morlet(epochs_induced_rare, freqs=freq, n_cycles=cycles, use_fft=True,
                            return_itc=False, decim=3, n_jobs=n_jobs, picks=config["pick"], average=True)

    power_induced_frequent= mne.time_frequency.tfr_morlet(epochs_induced_frequent, freqs=freq, n_cycles=cycles, use_fft=True,
                            return_itc=False, decim=3, n_jobs=n_jobs, picks=config["pick"], average=True)


    power_evoked_rare = mne.combine_evoked([power_rare, power_induced_rare],weights=[1,-1])
    power_evoked_frequent = mne.combine_evoked([power_frequent, power_induced_frequent],weights=[1,-1])

    difference_total = mne.combine_evoked([power_rare,power_frequent],weights=[1,-1])
    difference_evoked = mne.combine_evoked([power_evoked_rare,power_evoked_frequent],weights=[1,-1])
    difference_induced = mne.combine_evoked([power_induced_rare,power_induced_frequent],weights=[1,-1])

    # fig, axs = plt.subplots(1, 3)

    # #### Plot section ####

    # mode = "mean" #"percent"
    # baseline = (None, None)
    # cmin = -1e-9
    # cmax = -cmin
    # #baseline = None
    # #cmin = -5e-10
    # #cmax = -cmin
    # difference_total.plot(axes=axs[0],baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False,title="TF Total difference at {}".format(config["pick"]))
    # difference_evoked.plot(axes=axs[1], baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False,title="TF Evoked difference at {}".format(config["pick"]))
    # difference_induced.plot(axes=axs[2], baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False,title="1: TF Induced difference at {}".format(config["pick"]))
    # #fig_induced = difference_induced.plot(baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False,title="TF Difference Induced at {}".format(config["pick"]))

    fig2, axs2 = plt.subplots(1, 3)
    mode = "mean" #"percent"
    baseline = None
    cmin = None
    cmax = None
    #baseline = None
    #cmin = -5e-10
    #cmax = -cmin
    difference_total.plot(axes=axs2[0],baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False,title="TF Total difference at {}".format(config["pick"]))
    difference_evoked.plot(axes=axs2[1], baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False,title="TF Evoked difference at {}".format(config["pick"]))
    difference_induced.plot(axes=axs2[2], baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False,title="2: TF Induced difference at {}".format(config["pick"]))
    #fig_induced = difference_induced.plot(baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False,title="TF Difference Induced at {}".format(config["pick"]))
    addFigure(subject, fig2, "Total / Evoked / Induced  power (left-to-right)", "Time-Frequency")





    #plt.show()
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
    
    
    #difference_induced = mne.combine_evoked([power_induced_rare,power_induced_frequent],weights=[1,-1])



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
    plt.close('all')
    #power_total.plot_topo(show=False)

induced_rare_average = mne.combine_evoked(subjects_induced_rare_list, weights="equal")
induced_frequent_average = mne.combine_evoked(subjects_induced_frequent_list, weights="equal")

fig_suject_averages, axs = plt.subplots(1, 2)
induced_rare_average.plot(axes=axs[0], baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False,title="TF Induced difference at {}".format(config["pick"]))
induced_frequent_average.plot(axes=axs[1], baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False,title="TF Induced difference at {}".format(config["pick"]))
addFigure(subject, fig_suject_averages, "Average: Induced rare / Induced frequent power (left-to-right)", "Time-Frequency", totalReport=True)

induced_difference_average = mne.combine_evoked([induced_rare_average, induced_frequent_average], weights=[1,-1])
fig_difference_average = induced_frequent_average.plot(axes=axs2[2], baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False,title="TF Induced difference at {}".format(config["pick"]))
addFigure(subject, fig_suject_averages, "Average: Difference (left-to-right)", "Time-Frequency", totalReport=True)
plt.close('all')

stacked_tf = np.stack(subjects_tf_list)
stacked_zeros = np.stack(null_condition_list)
t_values, clusters, cluster_p_values, h0 = mne.stats.permutation_cluster_test([stacked_tf, stacked_zeros])
print("#################### Cluster permutation t-test: ###############\n", cluster_p_values)


############# plot permutation t test on average #################################
t_values, clusters, cluster_p_values, h0 = mne.stats.permutation_cluster_test([induced_difference_average._data, np.zeros(shape=induced_difference_average._data.shape)])
print("#################### Cluster permutation t-test: ###############\n", cluster_p_values)
times = 1e3 * induced_difference_average.times
plt.figure()
plt.subplots_adjust(0.12, 0.08, 0.96, 0.94, 0.2, 0.43)
plt.subplot(2, 1, 1)
freqs = np.arange(5, 55, 2)
T_obs_plot = np.nan * np.ones_like(t_values)
for c, p_val in zip(clusters, cluster_p_values):
    if p_val <= 0.05:
        T_obs_plot[c] = t_values[c]

plt.imshow(t_values,
           extent=[times[0], times[-1], freqs[0], freqs[-1]],
           aspect='auto', origin='lower', cmap='gray')
plt.imshow(T_obs_plot,
           extent=[times[0], times[-1], freqs[0], freqs[-1]],
           aspect='auto', origin='lower', cmap='RdBu_r')

plt.xlabel('Time (ms)')
plt.ylabel('Frequency (Hz)')
plt.title('Induced power')

ax2 = plt.subplot(2, 1, 2)
#TODO plot grand average instead of power spectrum
induced_difference_average.plot(axes=ax2, picks=config["pick"])

plt.show()


plt.show()