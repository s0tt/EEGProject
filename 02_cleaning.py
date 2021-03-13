import mne
from config import fname, bandpass_fmin, bandpass_fmax, n_jobs, nr_filt_cycles, subjects_numbers
import matplotlib.pyplot as plt
import numpy as np
##cleaning to be done manually


#print existing bads


## First subject
raw = mne.io.read_raw_fif(
    fname.filt(subject=subjects_numbers[0], run=1, fmin=bandpass_fmin, fmax=bandpass_fmax),
    preload=False)

print("Bads before cleaning:", raw.info['bads'])

fig = raw.plot(n_channels=len(raw.ch_names))#,scalings =40e-6)
plt.show()

print("Bads after cleaning:", raw.info['bads'])

