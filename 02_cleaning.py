import mne
from config import config, fname, n_jobs
import matplotlib.pyplot as plt
import numpy as np
from utils import *
from ccs_eeg_semesterproject import *
import os

subject = handleSubjectArg()

'''manual cleaning function'''
def manualCleaning(raw, subject):
    print("Open subject", subject, " for cleaning")
    fig = raw.plot(n_channels=len(raw.ch_names))
    plt.show()

    bad_ix = [i for i,a in enumerate(raw.annotations) if a['description']=="BAD_"]

    #little check to show that anotations were applied correctly
    print("Manual Annotations made: ", raw.annotations)
    

    #write manual annotations file if overwrite mode or file does not exist
    if config["isOverwrite"] or not os.path.isfile(f_cleanedTxt):
        raw.annotations[bad_ix].save(f_cleanedTxt)
    
'''interpolation of bad channels'''
def interpolateBads(raw):
    #interpolate bad channels if there exist some
    if len(raw.info['bads']) != 0:
        eeg_data = raw.copy()
        eeg_data.crop(tmin=0, tmax=5).pick_types(meg=False, eeg=True, exclude=[])
        eeg_data.annotations.crop(tmin=9, tmax=10) #little trick to remove the annotations from this plot data
        eeg_data_interp = eeg_data.copy().interpolate_bads(reset_bads=False)

        #VISUAL CHECK: interpolated channel check if the .interpolate_bads works as expected
        for title, data in zip(['before', 'after'], [eeg_data, eeg_data_interp]):
            fig = data.plot(butterfly=True, color='#00000022', bad_color='r', show=False, show_scalebars=False, show_scrollbars=False)
            fig.suptitle("Bad channel interpolation: "+title, size='xx-large', weight='bold')
            addFigure(subject, fig, "Bad channel interpolation: "+title, "Preprocess")

        raw.interpolate_bads()


f_filter = fname.filt(subject=subject)

#check if previous step (filtered raw file) exists
if os.path.isfile(f_filter):
    raw = readRawFif(f_filter, preload=False)


    f_cleanedTxt = fname.cleanedTxt(subject=subject)
    ### 1.Mode:  Manual Cleaning (if needed)
    if config["isDialogeMode"]:
        #ask user if manual cleaning shall be done again if file already exists
        if os.path.isfile(f_cleanedTxt) and not config["isOverwrite"]:
            user_in = input("Annotations for subject: " + str(subject) + " exist. Clean manual again ? (y/n)")
            if user_in == "y":    
                manualCleaning(raw, subject)
        else:
            manualCleaning(raw, subject)    

    ### 2.Mode: Use precomputed cleaned data
    if config["isPrecomputeMode"]:
        #just use provided cleaned data from semesterproject
        annotations,badChannels = load_precomputed_badData("local/bids", subject)
        if badChannels is not None:
            #catch 0 dimensional arrays and handle them with direct access
            if badChannels.ndim > 0: 
                ch_names = [raw.info.ch_names[idx] for idx in badChannels]
            else:
                ch_names = [raw.info.ch_names[badChannels]]
            raw.info['bads'].extend(ch_names)
        raw.annotations.append(annotations.onset,annotations.duration,annotations.description)
        interpolateBads(raw.load_data())

    ### 3.Mode: Use manual annotation file if it exists
    elif os.path.isfile(f_cleanedTxt): #check for existence of annotations
        annotations = mne.read_annotations(f_cleanedTxt)
        raw.annotations.append(annotations.onset,annotations.duration,annotations.description)

        if config["isDialogeMode"]:
            #Sanity check: interactive mode show loaded annotations to be sure they are correct
            fig = raw.plot(n_channels=len(raw.ch_names))
            plt.show()
        
        #interpolate bad channels if there exist some
        interpolateBads(raw)

    elif not config["isDialogeMode"]:
        raise RuntimeError("No annotationscould be obtained. Use either interactiveMode/preComputeMode or provide manual clean file")



    # generate report of compared epochs
    events,event_dict = mne.events_from_annotations(raw)
    keys = [e for e in event_dict.keys() if "stimulus" in e]
    event_dict_stim=dict((k, event_dict[k]) for k in keys if k in event_dict)

    epochs = getCodedEpochs(raw, reject_by_annotation=False)
    epochs_manual = getCodedEpochs(raw, reject_by_annotation=True)
    reject_criteria =  dict(eeg=config["reject_subject_config"]*(10**-6))
    epochs_thresh = getCodedEpochs(raw, reject=reject_criteria, reject_by_annotation=True)

    # compare different cleaning techniques, Compare with peak-to-peak just for reference --> is later neglected
    fig_evoked = mne.viz.plot_compare_evokeds({'Raw:':epochs.average(),'Manual Clean:':epochs_manual.average(),'Peak-To-Peak:':epochs_thresh.average()},picks=config["pick"], show=False)
    addFigure(subject, fig_evoked, "Evoked potential:", "Preprocess")

    #generate new data with annotations/delete old if selected
    raw.save(fname.cleaned(subject=subject), overwrite=True)
    if config["isSpaceSaveMode"]:
        os.remove(fname.filt(subject=subject))