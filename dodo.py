#TODO: Implement pipeline
from config import config, fname

def task_00_init():
    """Step 00: Init the system"""
    for subject in config["subjects_numbers"]:
        yield dict(
            name = subject,
            actions=["python 00_init.py {sub}".format(sub=subject)],
            targets=[fname.subject_dir(subject=subject)]
        )


def task_01_preprocess():
    """Step 01: Preprocess EEG data"""
    for subject in config["subjects_numbers"]:
        file_filter = fname.filt(subject=subject, run=1,
                   fmin=config["bandpass_fmin"], fmax=config["bandpass_fmax"])

        yield dict(
            name=subject,
            targets=[file_filter],
            actions=["python 01_preprocess.py {sub}".format(sub=subject)],
        )