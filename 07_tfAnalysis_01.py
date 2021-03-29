import argparse
import mne
import ccs_eeg_utils
from config import config, fname, n_jobs
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
from utils import *
import json, os
import numpy as np
import pickle

subject = handleSubjectArg()

difference_total_list = [] #array for time-frequency data for each subject induced. Dim: 40x (TF-Dim)
difference_induced_list = []
difference_evoked_list = []

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
difference_total.comment = "Condition difference total power | Sub: " + str(subject)
difference_evoked.comment = "Condition difference evoked power | Sub: " + str(subject)
difference_induced.comment = "Condition difference induced power | Sub: " + str(subject)

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

writeData(path=fname.tfAnalysis(subject=subject), data=[difference_total, difference_evoked, difference_induced])
#power_total.plot_topo(show=False)

