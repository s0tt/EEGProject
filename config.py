### File taken from https://github.com/AaltoImagingLanguage/conpy/blob/master/scripts/config.py
### all credits to Marijn van Vliet https://github.com/wmvanvliet
"""
Config file for EEG Project
"""

import os
from fnames import FileNames
import yaml
import mne

#check current user and paths, raise error if new user has not set a path
user = os.getlogin()
if user == 'so':
    study_path = 'C:\Git\EEGProject'
    n_jobs = 8
else:
    raise RuntimeError('Please adjust the config to your needs, before running')

##load YAML config to not polut namespace with python config variables
try:     
    with open("config.yaml", "r") as config_file:
        config = yaml.load(config_file.read(), Loader=yaml.Loader)
except yaml.YAMLError as err:
    raise IOError("Error reading yaml config")


fname = FileNames()

# Filenames for diretories
fname.add('study_path', study_path)
fname.add('archive_dir', '{study_path}/archive')
fname.add('subjects_dir', '{study_path}/subjects/{task}'.format(study_path=study_path, task=config["task"]))
fname.add('subject_dir', '{subjects_dir}/{subject}')
fname.add('log', '{subjects_dir}/mne-log.txt')


# Filenames for data files
fname.add('filt', '{subject_dir}/{subject}-filtered-raw_sss.fif')
fname.add('cleaned', '{subject_dir}/{subject}-cleaned-raw.fif')
# there seem to be problems with read anntoations in .csv format --> use .txt for now
fname.add('cleanedTxt', '{subject_dir}/{subject}-manual_clean-annotations.txt')
fname.add('ica', '{subject_dir}/{subject}-ica-raw.fif')
fname.add('reference', '{subject_dir}/{subject}-referenced-raw.fif')
fname.add('events','{study_path}/local/bids/sub-{subject}/ses-P3/eeg/sub-{subject}_ses-P3_task-P3_events.tsv' )
fname.add('eventCodes','{study_path}/local/bids/task-P3_events.json')
fname.add('evokedPeaks','{subject_dir}/evoked-peaks.json')
fname.add('epochs','{subject_dir}/{subject}-coded-epochs-epo.fif')
fname.add('evokedRare','{subject_dir}/evoked-rare-ave.fif')
fname.add('evokedFrequent','{subject_dir}/evoked-frequent-ave.fif')
fname.add('tfAnalysis', '{subject_dir}/{subject}-tf-power.pickel')
fname.add('decodingAnalysis', '{subject_dir}/{subject}-decode-peaks.pickel')

# Filenames for MNE reports
fname.add('reports_dir', '{study_path}/reports/{task}'.format(study_path=study_path, task=config["task"]))
fname.add('report', '{reports_dir}/{subject}-report.h5')
fname.add('report_html', '{reports_dir}/{subject}-report.html')
fname.add('totalReport', '{reports_dir}/total-report.h5')
fname.add('totalReport_html', '{reports_dir}/total-report.html')

# For FreeSurfer and MNE-Python to find the MRI data
os.environ["SUBJECTS_DIR"] = fname.subjects_dir

#set mne log level
mne.set_log_level(verbose="ERROR")
#mne.set_log_file(fname=fname.log())