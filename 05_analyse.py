import argparse
import mne
import ccs_eeg_utils
from config import config, fname, n_jobs
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
from utils import handleSubjectArg, readRawFif, addFigure
import json, os

# Handle command line arguments
subject = handleSubjectArg()

def getCodedEpochs(raw):
    evts,evts_dict = mne.events_from_annotations(raw)
    evt_plot = mne.viz.plot_events(evts, event_id=evts_dict, show=False)
    addFigure(subject, evt_plot, "Event overview", "Analyse")
    event_coding = config["event_coding"]
    coding_mapping = {}
    for coding_key in list(event_coding.keys()):
        wanted_codes = event_coding[coding_key]
        for key in evts_dict.keys():
            for code in wanted_codes:
                if(str(code) in key):
                    coding_mapping[str(coding_key)+"/"+str(code)] = evts_dict[key]
                
    return mne.Epochs(raw,evts,event_id=coding_mapping,tmin=-0.1,tmax=1)

raw = readRawFif(fname.reference(subject=subject))

epochs= getCodedEpochs(raw)

fig_rare_mean = epochs["rare"].plot_image(combine='mean', picks="Pz", show=False, title="Rare Stimulus")
fig_frequent_mean = epochs["frequent"].plot_image(combine='mean', picks="Pz", show=False, title="Frequent Stimulus")

rare_evoked = epochs["rare"]
frequent_evoked = epochs["frequent"]
difference_wave = mne.combine_evoked([rare_evoked.average(),
                                  frequent_evoked.average()],
                                 weights=[1, -1])

average = {"rare": rare_evoked.average(), "frequent": frequent_evoked.average(), "difference": difference_wave}

fig_evokeds = mne.viz.plot_compare_evokeds(average, picks="Pz", show=False)

#difference plot


# plot difference wave
difference_wave.plot_joint(times=[0.15], title='Rare - Frequent', picks="eeg", show=False)

addFigure(subject, fig_evokeds, "Evokeds for different conditions", "Analyse")

#plt.show()


def writeJson(json_dict):
    with open(fname.evokedPeaks, "w") as json_file:
        json.dump(json_dict, json_file, indent=4)

####extract evoked peaks for given subject
if not os.path.isfile(fname.evokedPeaks):
    writeJson(dict())

with open(fname.evokedPeaks) as json_file:
    evoked_peaks = json.load(json_file)
    subject_peaks = {}
    subject_peaks[subject] = {"rare": {}, "frequent": {}}
    subject_peaks[subject]["rare"]["peak"] = rare_evoked.load_data().pick("Pz").average().get_peak(ch_type="eeg")
    subject_peaks[subject]["frequent"]["peak"] = frequent_evoked.load_data().pick("Pz").average().get_peak(ch_type="eeg")
    evoked_peaks[subject] = subject_peaks[subject]
    writeJson(evoked_peaks)

#RQ: On which ERP-peaks do we find major difference between the conditions
#statistically test via linear regression
# name of predictors + intercept
# predictor_vars = ['face a - face b', 'phase-coherence', 'intercept']

# # # create design matrix
# meta = epochs.metadata.head()
# design = epochs.metadata[['phase-coherence', 'face']].copy()
# design['face a - face b'] = np.where(design['face'] == 'A', 1, -1)
# design['intercept'] = 1
# design = design[predictor_vars]

# reg = linear_regression(epochs_all,
#                         design_matrix=design,
#                         names=predictor_vars)

