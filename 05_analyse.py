import mne
from config import config, fname, n_jobs
from utils import *
import json, os
import numpy as np
import matplotlib.pyplot as plt

'''epoch plotting, both conditions side-by-side'''
def plotEpochs(epochs):
    fig, ax = plt.subplots(2, 4, constrained_layout=True, figsize=(16, 9), gridspec_kw={'width_ratios': [8, 1, 8, 1], 'height_ratios':[1,1]})
    epochs["cond1"].plot_image(axes=[ax[0][0], ax[1][0], ax[0][1]], picks="eeg", combine="mean", show=False)
    epochs["cond2"].plot_image(axes=[ax[0][2], ax[1][2], ax[0][3]], picks="eeg", combine="mean", show=False)
    cond = str(config["event_names"]["cond1"])
    ax[0][0].title.set_text("EEG (mean) for condition: " + config["event_names"]["cond1"])
    ax[0][2].title.set_text("EEG (mean) for condition: " + config["event_names"]["cond2"])
    ax[1][3].get_yaxis().set_visible(False)
    ax[1][3].get_xaxis().set_visible(False)
    ax[1][3].axis("off")
    ax[1][1].get_yaxis().set_visible(False)
    ax[1][1].get_xaxis().set_visible(False)
    ax[1][1].axis("off")
    return fig

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

# plot epochs per condition
fig_epoch =  plotEpochs(epochs)


#ERP plot
fig_evokeds = mne.viz.plot_compare_evokeds(average, picks=config["pick"], show=False)

# plot difference wave joint
fig_joint = difference_wave.plot_joint(title=cond1_name+ " - "+cond2_name, picks="eeg", show=False)


#plot topography for the ERP
all_times = np.arange(0, 0.8, 0.05)
fig_topo = difference_wave.plot_topomap(all_times, ch_type='eeg', time_unit='s',
                    ncols=8, nrows='auto', show=False)

addFigure(subject, fig_epoch, "Epochs of subject both conditions", "Analyse")
addFigure(subject, fig_evokeds, "Evokeds for different conditions", "Analyse")
addFigure(subject, fig_joint, "Difference wave joint", "Analyse")
addFigure(subject, fig_topo, "ERP Topography", "Analyse")

#write epoch objects
epochs.save(fname.epochs(subject=subject), overwrite=True, verbose=True)