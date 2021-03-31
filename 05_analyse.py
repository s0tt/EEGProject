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

epoch_cond1 = epochs["cond1"]
epoch_cond2 = epochs["cond2"]
cond1_name = config["event_names"]["cond1"]
cond2_name = config["event_names"]["cond2"]

evoked_cond1 = epoch_cond1.average()
evoked_cond2 = epoch_cond2.average()

difference_wave = mne.combine_evoked([evoked_cond1,
                                  evoked_cond2],
                                 weights=[1, -1])

average = {cond1_name: evoked_cond1, cond2_name: evoked_cond2, "difference": difference_wave}

# plot epochs per condition
fig_epoch =  plotEpochs(epochs)


#ERP plot
fig_evokeds = mne.viz.plot_compare_evokeds(average, picks=config["pick"], show=False)

# plot difference wave joint
fig_joint = difference_wave.plot_joint(title=cond1_name+ " - "+cond2_name, picks="eeg", show=False)


#plot topography for the conditions and ERP
all_times = np.arange(epochs.baseline[0], 0.9, 0.05)

fig_topo_cond1= evoked_cond1.plot_topomap(all_times, ch_type=config["analyse_pick"], time_unit='s',
                    ncols=8, nrows='auto', show=False)
fig_topo_cond2 = evoked_cond2.plot_topomap(all_times, ch_type=config["analyse_pick"], time_unit='s',
                    ncols=8, nrows='auto', show=False)
fig_topo_diff = difference_wave.plot_topomap(all_times, ch_type=config["analyse_pick"], time_unit='s',
                    ncols=8, nrows='auto', show=False)

addFigure(subject, fig_epoch, "Epochs of subject both conditions", "Analyse")
addFigure(subject, fig_evokeds, "Evokeds for different conditions", "Analyse")
addFigure(subject, fig_joint, "Difference wave joint", "Analyse")
addFigure(subject, fig_topo_cond1, "Topography condition: {} at pick: {}".format(cond1_name, config["analyse_pick"]), "Analyse")
addFigure(subject, fig_topo_cond2, "Topography condition: {} at pick: {}".format(cond2_name, config["analyse_pick"]), "Analyse")
addFigure(subject, fig_topo_diff, "Difference wave Topography at {}".format(config["analyse_pick"]), "Analyse")

#write epoch objects
epochs.save(fname.epochs(subject=subject), overwrite=True, verbose=True)