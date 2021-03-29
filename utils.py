import mne
from mne_bids import (BIDSPath, read_raw_bids)
import ccs_eeg_utils
import json
import re
import argparse
from config import config, fname
import warnings
import numpy as np
import pickle

def readRawData(subject_id,task=config["task"],session=config["task"], datatype='eeg', suffix='eeg', bids_root="local/bids"):
    bids_path = BIDSPath(subject=subject_id,task=config["task"],session=config["task"],
                     datatype='eeg', suffix='eeg',
                     root=bids_root)
    raw = read_raw_bids(bids_path)
    #fix the annotations readin
    ccs_eeg_utils.read_annotations_core(bids_path,raw)
    raw.load_data()
    return raw

def readRawFif(fname, **kwargs):
    # Load raw data
    try:
        raw = mne.io.read_raw_fif(fname, **kwargs)

        # add missing channel types
        raw.set_channel_types({'HEOG_left': 'eog', 'HEOG_right': 'eog',  'VEOG_lower': 'eog' })
        
        # set montage 
        raw.set_montage('standard_1020',match_case=False, on_missing="ignore")

        return raw
    except FileNotFoundError:
        print("File to load not found. Did you run the previous steps?")

def readEventCoding():
    oddBallIds = []
    normalLetterIds = []

    with open(fname.eventCodes) as f:
        data = json.load(f)

    enc_dict = data["value"]["Levels"]
    for key in list(enc_dict.keys()):
        re_search = re.search(r".*block.*target.*([A-E]).*trial.*stimulus.*([A-E]).*", enc_dict[key])
        if re_search:
            if re_search.group(1) == re_search.group(2):
                oddBallIds.append(key)
            else:
                normalLetterIds.append(key)

def addFigure(sub, fig, caption, section, totalReport=False, **kwargs):
    if totalReport:
        f_report = fname.totalReport
        f_report_html = fname.totalReport_html
    else:
        f_report = fname.report(subject=sub)
        f_report_html = fname.report_html(subject=sub)
    
    with mne.open_report(f_report) as report:
        report.add_figs_to_section(
            fig,
            captions=caption,
            section=section,
            replace=True,
            **kwargs
        )
        report.save(f_report_html, overwrite=True,
                    open_browser=False)
    
def handleSubjectArg(multiSub=False):
    parser = argparse.ArgumentParser(description=__doc__)

    if multiSub:
        parser = argparse.ArgumentParser()
        parser.add_argument('subjects',metavar='subs', nargs='+',help='Subject list')
        args = parser.parse_args()
        subjects = args.subjects
    else:
        parser.add_argument('subject', metavar='sub', help='Subject to process')
        args = parser.parse_args()
        subjects = args.subject
    print('Processing subjects:', subjects)
    return subjects

def getCodedEpochs(raw, printPlot=False, subject=None, **kwargs):
    evts,evts_dict = mne.events_from_annotations(raw)
    evt_plot = mne.viz.plot_events(evts, event_id=evts_dict, show=False)
    if printPlot:
        addFigure(subject, evt_plot, "Event overview before removal", "Analyse") 

    ##### Remove epochs where reponse to stimulus has a wrong code (e.g. 202)
    events_dict_inv = {value: key for key, value in evts_dict.items()}

    #Assert correct inversion
    assert len(evts_dict) == len(events_dict_inv)

    wrong_response_code = config["event_coding"]["response"][1]
    wrong_event_ids = evts_dict[f"response:{wrong_response_code}"]
    wrong_events = []
    if evts[0][2] == wrong_event_ids:
        wrong_events.append(0)

    #Check for all events if wrong response happened
    for i in range(len(evts)-1):
        if evts[i+1][2] == wrong_event_ids:
            prev_event_id = evts[i][2]
            prev_event_type = events_dict_inv[prev_event_id]
            if prev_event_type.startswith("stimulus"):
                # Mark event with stimulus that caused wrong response
                wrong_events.append(i)
            # Mark event with wrong response
            wrong_events.append(i+1)

    #Update events&event dict
    evts = np.delete(evts, wrong_events, axis=0)
    evts_dict = dict((key,value) for key, value in evts_dict.items() if value in evts[:,2])
    evt_plot = mne.viz.plot_events(evts, event_id=evts_dict, show=False)
    if printPlot:
        addFigure(subject, evt_plot, "Event overview after removal", "Analyse")

    #Check if cleaning successful 
    assert evts[:,2].all() != wrong_event_ids

    ###### Adapt event coding #####
    event_coding = config["event_coding"]
    coding_mapping = {}
    for coding_key in list(event_coding.keys()):
        wanted_codes = event_coding[coding_key]
        for key in evts_dict.keys():
            for code in wanted_codes:
                if(str(code) == key.split(":")[1]):
                    coding_mapping[str(coding_key)+"/"+str(code)] = evts_dict[key]

    #issue warning for missing bad segment annotations before returning the Epoch object if no BAD_ tag is found
    if not any(description.startswith('BAD_') for description in raw.annotations.description):
        warnings.warn("No BAD_ segments found. Is this intended?")
    return mne.Epochs(raw,evts,event_id=coding_mapping,tmin=-0.1,tmax=1, **kwargs)

def readData(path):
    with open(path, "rb") as pickle_file:
        data = pickle.load(pickle_file)
        pickle_file.close()
        return data
    
def writeData(path, data):
    with open(path, "wb") as pickle_file:
        pickle.dump(data, pickle_file)
        pickle_file.close()
