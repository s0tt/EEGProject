import mne
from config import config, fname, n_jobs
from utils import *
import json, os
import numpy as np

# Handle command line arguments
subject = handleSubjectArg()

raw = readRawFif(fname.reference(subject=subject))

#get event coded epochs, bad channels are by default removed by MNE
epochs= getCodedEpochs(raw, printPlot=True, subject=subject, reject_by_annotation=True)

cond1_evoked = epochs["cond1"]
cond2_evoked = epochs["cond2"]
cond1_name = config["event_names"]["cond1"]
cond2_name = config["event_names"]["cond2"]

difference_wave = mne.combine_evoked([cond1_evoked.average(),
                                  cond2_evoked.average()],
                                 weights=[1, -1])

average = {cond1_name: cond1_evoked.average(), cond2_name: cond2_evoked.average(), "difference": difference_wave}

#ERP plot
fig_evokeds = mne.viz.plot_compare_evokeds(average, picks=config["pick"], show=False)

# plot difference wave joint
fig_joint = difference_wave.plot_joint(title=[cond1_name, " - ", cond2_name], picks="eeg", show=False)

addFigure(subject, fig_evokeds, "Evokeds for different conditions", "Analyse")
addFigure(subject, fig_joint, "Difference wave joint", "Analyse")

#write epoch objects
epochs.save(fname.epochs(subject=subject), overwrite=True, verbose=True)