### File taken from https://github.com/AaltoImagingLanguage/conpy/blob/master/scripts/config.py
### all credits to Marijn van Vliet https://github.com/wmvanvliet
"""
===========
Config file
===========

Configuration parameters for the study.
"""

import os
from socket import getfqdn
from fnames import FileNames

user = os.getlogin()

if user == 'so':
    study_path = 'C:\Git\EEGProject'
    n_jobs = 8
else:
    raise RuntimeError('Please adjust the config to your needs, before running')

#subjects to analyse
subjects_numbers = ["002", "019", "037"]

# Band-pass filter limits
bandpass_fmin = 0.5  # Hz
bandpass_fmax = 50  # Hz
nr_filt_cycles = 1 #nr of filter cycles

fname = FileNames()

# Filenames for diretories
fname.add('study_path', study_path)
fname.add('archive_dir', '{study_path}/archive')
fname.add('subjects_dir', '{study_path}/subjects')
fname.add('subject_dir', '{subjects_dir}/{subject}')

# Filenames for data files
fname.add('filt', '{subject_dir}/run_{run:02d}-filt-{fmin}-{fmax}-raw_sss.fif')
fname.add('ica', '{subject_dir}/{subject}-ica.fif')

# Filenames for MNE reports
fname.add('reports_dir', '{study_path}/reports/')
fname.add('report', '{reports_dir}/{subject}-report.h5')
fname.add('report_html', '{reports_dir}/{subject}-report.html')

# For FreeSurfer and MNE-Python to find the MRI data
os.environ["SUBJECTS_DIR"] = fname.subjects_dir
