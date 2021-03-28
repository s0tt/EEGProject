import mne
from config import config, fname, n_jobs
from utils import *
import json, os
import numpy as np

# Handle command line arguments
subject = handleSubjectArg()

raw = readRawFif(fname.reference(subject=subject))

epochs= getCodedEpochs(raw, printPlot=True, subject=subject, reject_by_annotation=True)

# fig_rare_mean = epochs["rare"].plot_image(combine='mean', picks=config["pick"], show=False, title="Rare Stimulus")
# fig_frequent_mean = epochs["frequent"].plot_image(combine='mean', picks=config["pick"], show=False, title="Frequent Stimulus")

rare_evoked = epochs["rare"]
frequent_evoked = epochs["frequent"]
difference_wave = mne.combine_evoked([rare_evoked.average(),
                                  frequent_evoked.average()],
                                 weights=[1, -1])

average = {"rare": rare_evoked.average(), "frequent": frequent_evoked.average(), "difference": difference_wave}

#ERP plot
fig_evokeds = mne.viz.plot_compare_evokeds(average, picks=config["pick"], show=False)

# plot difference wave joint
fig_joint = difference_wave.plot_joint(times=[0.15], title='Rare - Frequent', picks="eeg", show=False)

addFigure(subject, fig_evokeds, "Evokeds for different conditions", "Analyse")
addFigure(subject, fig_joint, "Difference wave joint", "Analyse")

#write epoch objects
epochs.save(fname.epochs(subject=subject), overwrite=True)