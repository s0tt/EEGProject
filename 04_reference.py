import argparse
import mne
from ccs_eeg_semesterproject import *
import ccs_eeg_utils
from config import config, fname, n_jobs
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
    raw.set_eeg_reference('average', projection=True)
    #TODO: Later compare several reference methods
    #raw.set_eeg_reference(ref_channels=["P9", "P10"])
    raw.save(fname.reference(subject=subject), overwrite=True)
    if config["isSpaceSaveMode"]:
        os.remove(fname.ica(subject=subject, bads = str(list(config["subject_ica_channels"][subject]))))

raw = readRawFif(fname.ica(subject=subject, bads = str(list(config["subject_ica_channels"][subject]))), preload=True)
rereference(raw, subject)
fig, axes = plt.subplots(1, 2)
for title, proj, axis in zip(['Original', 'Average'], [False, True], axes):
    axis = raw.plot(proj=proj, n_channels=len(raw), show=False)
    # make room for title
    axis.subplots_adjust(top=0.9)
    axis.suptitle('{} reference'.format(title))
addFigure(subject, fig, "Comparison original/ average referenced:", "Preprocess")