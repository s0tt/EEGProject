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

''' function for rereferencing EEG data'''
def rereference(raw, subject):
    #reference as projection, do not change data directly
    raw.set_eeg_reference(ref_channels=config["reference"], projection=True if config["reference"] == "average" else False)

    raw.save(fname.reference(subject=subject), overwrite=True)
    if config["isSpaceSaveMode"]:
        os.remove(fname.ica(subject=subject))

''' plots rereference figures before/after'''
def plotRereference(raw, title, project=False):
    fig, ax = plt.subplots(1, 3, figsize=(9, 5), gridspec_kw={'width_ratios': [15, 5, 1]})
    epochs = getCodedEpochs(raw)
    evoked = epochs.average()
    title = title
    evoked.plot(axes=ax[0], titles=dict(eeg=title), time_unit='s', proj=project, show=False)
    evoked.plot_topomap(axes=[ax[1],ax[2]], times=[0.35], size=2.5, title=title, time_unit='s', proj=project, show=False)
    fig.subplots_adjust(bottom=0.15, left=0.15)
    return fig


#load raw object ob previous step
raw = readRawFif(fname.ica(subject=subject), preload=True)

if config["reference"] != "average":
    fig_before = plotRereference(raw, "Before referencing")

#perform referencing
rereference(raw, subject)

if config["reference"] == "average":
    fig_before = plotRereference(raw, "Before referencing", project=False)


fig_after = plotRereference(raw, "After referencing", project=True)

addFigure(subject, fig_before, "Before referencing:", "Preprocess")
addFigure(subject, fig_after, "After referencing:", "Preprocess")