from utils import *
from config import config, fname, n_jobs

# Handle command line arguments
subject = handleSubjectArg()

figs_before = []
figs_after = []

# Read data from last step
raw = readRawData(subject_id=subject)

#bandpass filter raw EEG data
### Best-pratices/Recommendations from: Digital filter design for electrophysiological data – a practical approach ###
# - Low-pass filters with cutoff frequencies > 40 Hz during ERP analysis
# - Showed that high-pass cutoff frequency ~0.75Hz has only minor effects on ERP --> Therefore stay below ~0.75Hz to not disturb signal
# - Better use bandpass instead of separate Low & High-Pass
# - FIR filters are easier to controll, always stable, well-defined passband etc. in comparison to IIR
# --> These recommendations lead to my chosen filter
### From MNE docs:
# "firwin” uses a time-domain design technique that generally gives improved attenuation using fewer samples than “firwin2”

raw_filt = raw.copy().filter(
        config["bandpass_fmin"], config["bandpass_fmax"], l_trans_bandwidth='auto',
        h_trans_bandwidth='auto', filter_length='auto', phase='zero',
        fir_window='hamming', fir_design='firwin', n_jobs=n_jobs)

#visual check filter before/after
figs_before.append(raw.plot_psd(show=False, fmin=0, fmax=150))
figs_after.append(raw_filt.plot_psd(show=False, fmin=0, fmax=150))
figs_before[0].subplots_adjust(bottom=0.15)
figs_after[0].subplots_adjust(bottom=0.15)
f = fname.filt(subject=subject)
raw_filt.save(f, overwrite=True)

# Append PDF plots to report
addFigure(subject, figs_before, "PSD before filtering:", "Preprocess")
addFigure(subject, figs_after, "PSD after filtering:", "Preprocess")