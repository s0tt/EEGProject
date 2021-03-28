import argparse
import mne
import ccs_eeg_utils
from config import config, fname, n_jobs
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
from utils import handleSubjectArg, readRawFif, addFigure
import json, os
import numpy as np

# parser = argparse.ArgumentParser()
# parser.add_argument('subjects',metavar='subs', nargs='+',help='Subject list')
# args = parser.parse_args()
# subjects = args.subjects
subject = handleSubjectArg()


epochs = mne.read_epochs(fname.epochs(subject=subject))
evoked_difference = mne.combine_evoked([epochs["rare"].average(),epochs["frequent"].average()],weights=[1, -1])
epochs_induced = epochs.copy().subtract_evoked(evoked=evoked_difference)

#plot power spectrum
fig_psd = epochs.plot_psd(fmin=2., fmax=40., average=True, spatial_colors=False, show=False)
addFigure(subject, fig_psd, "Power spectrum of epochs", "Time-Frequency")

f, ax = plt.subplots()
psds, freqs = mne.time_frequency.psd_multitaper(epochs, fmin=2, fmax=40, n_jobs=1, picks=config["pick"])
psds = 10. * np.log10(psds)
psds_mean = psds.mean(0).mean(0)
psds_std = psds.mean(0).std(0)

ax.plot(freqs, psds_mean, color='k')
ax.fill_between(freqs, psds_mean - psds_std, psds_mean + psds_std,
                color='k', alpha=.5)
ax.set(title='Multitaper PSD', xlabel='Frequency (Hz)',
       ylabel='Power Spectral Density (dB)')



# define frequencies to analyse(log-spaced)

freqs = [np.logspace(*np.log10([5, 80]), num=25), np.logspace(*np.log10([5, 80]), num=25)]
n_cycles = [1, freqs[1] / 2.] #cycles frequency wise

for freq, cycles in zip(freqs, n_cycles):
    power_total= mne.time_frequency.tfr_morlet(epochs, freqs=freq, n_cycles=cycles, use_fft=True,
                            return_itc=False, decim=3, n_jobs=6, picks=config["pick"])

    power_induced= mne.time_frequency.tfr_morlet(epochs_induced, freqs=freq, n_cycles=cycles, use_fft=True,
                            return_itc=False, decim=3, n_jobs=6, picks=config["pick"])
    power_evoked = mne.combine_evoked([power_total,power_induced],weights=[1,-1])
    mode = "percent"
    baseline = [-0.5,0]
    cmin = -3
    cmax = 3
    power_total.plot(baseline=baseline,picks=config["pick"], mode=mode,vmin=cmin,vmax=cmax, show=False, title="TF Total at {}".format(config["pick"]))
    power_induced.plot(baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False,title="TF Induced at {}".format(config["pick"]))
    power_evoked.plot(baseline=baseline,picks=config["pick"],mode=mode,vmin=cmin,vmax=cmax, show=False,title="TF Evoked at {}".format(config["pick"]))

power_total.plot_topo(show=False)

plt.show()