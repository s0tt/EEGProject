import argparse
import mne
import ccs_eeg_utils
from config import config, fname, n_jobs
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
from utils import handleSubjectArg, readRawFif, addFigure

# Handle command line arguments
subject = handleSubjectArg()

def readEpochs(raw, evt_type):
    evts,evts_dict = mne.events_from_annotations(raw)
    if evt_type == "rare": #odball stimuli
        wanted_codes = config["oddball_codes"]
    if evt_type == "frequent": #normal letter stimuli
        wanted_codes = config["frequent_codes"]
    if evt_type == "all":
        wanted_codes = config["oddball_codes"]+config["frequent_codes"]

    wanted_codes = wanted_codes+config["response_codes"]
    wanted_event_keys = [key for key in evts_dict.keys() if any(str(code) in key for code in wanted_codes)]
    final_evts=dict((k, evts_dict[k]) for k in wanted_event_keys if k in evts_dict)
    epochs = mne.Epochs(raw,evts,final_evts,tmin=-0.1,tmax=1)
    return epochs

raw = readRawFif(fname.reference(subject=subject))

evts,evts_dict = mne.events_from_annotations(raw)
epochs_rare = readEpochs(raw, "rare")
fig_rare_mean = epochs_rare.plot_image(combine='mean', picks="Pz", show=False, title="Rare Stimulus")

epochs_freq = readEpochs(raw, "frequent")
fig_frequent_mean = epochs_freq.plot_image(combine='mean', picks="Pz", show=False, title="Frequent Stimulus")

average = {"rare": epochs_rare.average(), "frequent": epochs_freq.average()}

mne.viz.plot_compare_evokeds(average, picks="Pz")

#difference plot
difference_wave = mne.combine_evoked([epochs_rare.average(),
                                  epochs_freq.average()],
                                 weights=[1, -1])

# plot difference wave
difference_wave.plot_joint(times=[0.15], title='Rare - Frequent')

evt_plot = mne.viz.plot_events(evts, event_id=evts_dict, show=False)
addFigure(subject, evt_plot, "Event overview", "Analyse")
addFigure(subject, fig_rare_mean, "Mean of rare (oddball) stimulus", "Analyse")
addFigure(subject, fig_frequent_mean, "Mean of frequent stimulus", "Analyse")

plt.show()


#RQ: On which ERP-peaks do we find major difference between the conditions
#statistically test via linear regression
# name of predictors + intercept
# predictor_vars = ['face a - face b', 'phase-coherence', 'intercept']

# # create design matrix
# epochs_all = readEpochs(raw, "all")
# design = epochs_all.metadata[['phase-coherence', 'face']].copy()
# design['face a - face b'] = np.where(design['face'] == 'A', 1, -1)
# design['intercept'] = 1
# design = design[predictor_vars]

# reg = linear_regression(epochs_all,
#                         design_matrix=design,
#                         names=predictor_vars)

