#TODO: Implement pipeline
from config import config, fname

all_subjects = [str(sub).zfill(3) for sub in range(1,41)]

###set which subjects to compute
#subjects = config["subjects_numbers"]
subjects = all_subjects

def task_00_init():
    """Step 00: Init the system"""
    for subject in subjects:
        yield dict(
            name = subject,
            actions=["python 00_init.py {sub}".format(sub=subject)],
            targets=[fname.subject_dir(subject=subject)]
        )


def task_01_preprocess():
    """Step 01: Preprocess EEG data by filtering"""
    for subject in subjects:
        file_filter = fname.filt(subject=subject,
                   fmin=config["bandpass_fmin"], fmax=config["bandpass_fmax"])

        yield dict(
            name=subject,
            targets=[file_filter],
            actions=["python 01_preprocess.py {sub}".format(sub=subject)],
        )

def task_02_clean():
    """Step 02: clean data either manually or auto"""
    for subject in subjects:
        yield dict(
            name=subject,
            targets=[fname.cleaned(subject=subject)],
            actions=["python 02_cleaning.py {sub}".format(sub=subject)],
        )

def task_03_ica():
    """Step 03: ICA analysis to identify bad components"""
    for subject in subjects:
        yield dict(
            name=subject,
            targets=[fname.ica(subject=subject, bads = str(list(config["subject_ica_channels"][subject])))],
            actions=["python 03_ica.py {sub}".format(sub=subject)],
        )

def task_04_reference():
    """Step 04: clean data either manually or auto"""
    for subject in subjects:
        yield dict(
            name=subject,
            targets=[fname.reference(subject=subject)],
            actions=["python 04_reference.py {sub}".format(sub=subject)],
        )