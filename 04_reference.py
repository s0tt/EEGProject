import argparse
import mne
from ccs_eeg_semesterproject import *
import ccs_eeg_utils
from config import *
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
from utils import *

# Handle command line arguments
subject = handleSubjectArg()

#Rereference to average as recommended here:
# https://www.fieldtriptoolbox.org/faq/why_should_i_use_an_average_reference_for_eeg_source_reconstruction/
# https://mne.tools/stable/auto_tutorials/preprocessing/plot_55_setting_eeg_reference.html 
#
# For P300 the reference electrodes are offline referenced to P9&P10
# as it is described in the ERP Core paper:
# "
# For analysis of the MMN, N2pc, N400, P3, LRP, and ERN, the EEG signals were referenced offline to the average of P9 and P10 (located adjacent to the mastoids); 
# we find that P9 and P10 provide cleaner signals than the traditional mastoid sites, but the resulting waveforms are otherwise nearly identical to mastoid- referenced data.
# "
# "If you plan to perform source modeling (either with EEG or combined EEG/MEG data), it is strongly recommended to use the average-reference-as-projection approach."
# --> Still use average reference projection as it spreads forwards modeling error evenly
def rereference(raw, subject):
    #raw.set_eeg_reference('average', projection=True)
    raw.set_eeg_reference(ref_channels=["P9", "P10"])
    raw.save(fname.reference(subject=subject), overwrite=True)

if config["isPrecomputeMode"]:
    ### switch to precomputed semesterproject data
    annotations,badChannels = load_precomputed_badData("local/bids", subject)
    raw = readRawData(subject_id=subject)
    raw.set_channel_types({'HEOG_left': 'eog', 'HEOG_right': 'eog',  'VEOG_lower': 'eog' })
    raw.set_montage('standard_1020',match_case=False, on_missing="ignore")
    raw.annotations.append(annotations.onset,annotations.duration,annotations.description)
    raw.interpolate_bads(badChannels)
    raw_filt = raw.filter(config["bandpass_fmin"], config["bandpass_fmax"], l_trans_bandwidth='auto',
            h_trans_bandwidth='auto', filter_length='auto', phase='zero',
            fir_window='hamming', fir_design='firwin', n_jobs=n_jobs)
    ica, bad_components = load_precomputed_ica("local/bids", subject)
    raw_ica = ica.apply(raw_filt, exclude=bad_components.astype(int))
    rereference(raw_ica, subject)
    print("Loaded precomputed project data for sub: ", subject)

else:
    raw = readRawFif(fname.ica(subject=subject, bads = str(list(config["subject_ica_channels"][subject]))), preload=True)
    rereference(raw, subject)
    fig, axes = plt.subplots(1, 2)
    for title, proj, axis in zip(['Original', 'Average'], [False, True], axes):
        axis = raw.plot(proj=proj, n_channels=len(raw), show=False)
        # make room for title
        axis.subplots_adjust(top=0.9)
        axis.suptitle('{} reference'.format(title))
    addFigure(subject, fig, "Comparison original/ average referenced:", "Preprocess")