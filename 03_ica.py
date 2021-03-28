import mne
from ccs_eeg_semesterproject import *
from config import config, fname, n_jobs
from utils import *

# Handle command line arguments
subject = handleSubjectArg()

# Load raw data of previous step
raw = readRawFif(fname.cleaned(subject=subject), preload=True)
raw_cleaned = raw.copy() #keep copy for overlay plot

if config["isPrecomputeMode"]:
    ica, bad_components = load_precomputed_ica("local/bids", subject)
    raw_ica = ica.apply(raw, exclude=np.array(bad_components).astype(int))

else:
    ica = mne.preprocessing.ICA(n_components=config["nr_ica_components"], random_state=97, max_iter=800, method=config["ica_method"])

    #ica specific high-pass filter with ~1hz to remove slow drifts
    # according to: https://mne.tools/dev/auto_tutorials/preprocessing/plot_40_artifact_correction_ica.html
    # and https://mne.tools/stable/generated/mne.preprocessing.ICA.html 
    
    raw_filt = raw.copy()
    raw_filt.load_data().filter(l_freq=config["freq_highpass_ica"], h_freq=None)

    ica.fit(raw_filt, verbose=True)

    #Apply ICA to original raw data after components are found only if bad channels specified in config
    assert subject in config["subject_ica_channels"]
    bad_components = config["subject_ica_channels"][subject]
    raw_ica = ica.apply(raw, exclude=np.array(bad_components).astype(int))

    #manually look at components and identify independent components
    # according to: https://labeling.ucsd.edu/tutorial/labels
    fig_components = ica.plot_components(show=True if config["isDialogeMode"] else False)

    fig_reject_components = []

    if config["isDialogeMode"]:
        ica.plot_properties(raw, picks=range(config["nr_ica_components"]), show=True)

    for component in config["subject_ica_channels"][subject]:
        break #fig_reject_components.append(ica.plot_properties(raw, picks=[component],show=False)) TODO: find solution to plot this 3d interactive object to report
    
    #VISUAL CHECK: add ICA components to subject report
    addFigure(subject, fig_components, "ICA Component overview:", "Preprocess")

#save ICA data
f_ica = fname.ica(subject=subject)
raw_ica.save(f_ica, overwrite=True)

if config["isSpaceSaveMode"]:
    os.remove(fname.cleaned(subject=subject))

#VISUAL CHECK: plot ICA for overlay of cleaned signal
fig_overlay = ica.plot_overlay(raw_cleaned,exclude=np.array(bad_components).astype(int), show=False)
addFigure(subject, fig_overlay, "Overlay original/reconstructed:", "Preprocess")