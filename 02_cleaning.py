import mne
#from config import fname, bandpass_fmin, bandpass_fmax, n_jobs, nr_filt_cycles, subjects_numbers
import config
from config import *
import matplotlib.pyplot as plt
import numpy as np


##cleaning to be done manually
def manualCleaning():
    print("Open subject", subject, " for cleaning")
    fig = raw.plot(n_channels=len(raw.ch_names))
    plt.show()

    bad_ix = [i for i,a in enumerate(raw.annotations) if a['description']=="BAD_"]
    print("Annotations: ", raw.annotations)
    

    #write file if overwrite mode or file does not exist
    if isOverwrite or not os.path.isfile(f_cleanedTxt) or user_in == "y":
        raw.annotations[bad_ix].save(f_cleanedTxt)

    
    # f_cleanedFif = fname.cleaned(subject=subject)
    # raw.save(f_cleanedFif, overwrite=isOverwrite)y
    

#Iterate over subjects
for subject in subjects_numbers:
    try:
        raw = mne.io.read_raw_fif(
            fname.filt(subject=subject, run=1, fmin=bandpass_fmin, fmax=bandpass_fmax),
            preload=False)
    except FileNotFoundError:
        print("Filtered data for subject ", subject, "not found. First run 01_preprocessing")

    ### 1. Manual Cleaning (if needed)
    f_cleanedTxt = fname.cleanedTxt(subject=subject)

    ###Check which mode for cleaning
    if isDialogeMode:
        if os.path.isfile(f_cleanedTxt) and not isOverwrite:
            user_in = input("Annotations for subject: " + str(subject) + " exist. Clean manual again ? (y/n)")
            if user_in == "y":    
                manualCleaning()
        else:
            manualCleaning()    

    ### 2. interpolate
    if os.path.isfile(f_cleanedTxt): #check for existence of annotations
        annotations = mne.read_annotations(f_cleanedTxt)
        raw.annotations.append(annotations.onset,annotations.duration,annotations.description)

        if isDialogeMode:
            #Sanity check: interactive mode show loaded annotations
            fig = raw.plot(n_channels=len(raw.ch_names))
            plt.show()
        
        #interpolate bad channels if there exist some
        if len(raw.info['bads']) != 0:
            raw.set_montage('standard_1020',match_case=False)
            raw.interpolate_bads()


    ### 3. generate report of compared epochs
    events,event_dict = mne.events_from_annotations(raw)
    keys = [e for e in event_dict.keys() if "stimulus" in e]
    event_dict_stim=dict((k, event_dict[k]) for k in keys if k in event_dict)
    epochs = mne.Epochs(raw,events,event_dict_stim,tmin=-0.1,tmax=1,reject_by_annotation=False)
    epochs_manual = mne.Epochs(raw,events,event_dict_stim,tmin=-0.1,tmax=1,reject_by_annotation=True)
    reject_criteria =  reject_suject_config[subject]
    epochs_thresh = mne.Epochs(raw,events,event_dict_stim,tmin=-0.1,tmax=1,reject=reject_criteria,reject_by_annotation=False)

    #from matplotlib import pyplot as plt
    # compare
    fig_evoked = mne.viz.plot_compare_evokeds({'Raw:':epochs.average(),'Manual Clean:':epochs_manual.average(),'Peak-To-Peak:':epochs_thresh.average()},picks="Pz", show=False)

        # Append PDF plots to report
    with mne.open_report(fname.report(subject=subject)) as report:
        report.add_figs_to_section(
            fig_evoked,
            captions=["Evoked potential:"],
            section='Sensor-level',
            replace=True
        )
        report.save(fname.report_html(subject=subject), overwrite=True,
                    open_browser=False)