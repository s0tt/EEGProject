#TODO: Implement pipeline
from config import config, fname

all_subjects = [str(sub).zfill(3) for sub in range(1,41)]#[1, 3, 4, 5, 6]]

###set which subjects to compute
#subjects = config["subjects_numbers"]
subjects = all_subjects

def task_00_init():
    """Step 00: Init the system"""
    for subject in subjects:
        yield dict(
            name = subject,
            actions=["python 00_init.py {sub}".format(sub=subject)],
            targets=[fname.subject_dir(subject=subject)],
            uptodate=[True]
        )


def task_01_preprocess():
    """Step 01: Preprocess EEG data by filtering"""
    for subject in subjects:
        yield dict(
            name=subject,
            targets=[fname.filt(subject=subject,fmin=config["bandpass_fmin"], fmax=config["bandpass_fmax"])],
            actions=["python 01_preprocess.py {sub}".format(sub=subject)],
            uptodate=[True],
            clean=True  
        )

def task_02_clean():
    """Step 02: clean data either manually or auto"""
    for subject in subjects:
        yield dict(
            name=subject,
            targets=[fname.cleaned(subject=subject)],
            actions=["python 02_cleaning.py {sub}".format(sub=subject)],
            file_dep=[fname.filt(subject=subject,fmin=config["bandpass_fmin"], fmax=config["bandpass_fmax"])],
            clean=True
        )

def task_03_ica():
    """Step 03: ICA analysis to identify bad components"""
    for subject in subjects:
        yield dict(
            name=subject,
            targets=[fname.ica(subject=subject)],
            actions=["python 03_ica.py {sub}".format(sub=subject)],
            file_dep=[fname.cleaned(subject=subject)],
            clean=True
        )

def task_04_reference():
    """Step 04: clean data either manually or auto"""
    for subject in subjects:
        yield dict(
            name=subject,
            targets=[fname.reference(subject=subject)],
            actions=["python 04_reference.py {sub}".format(sub=subject)],
            file_dep=[fname.ica(subject=subject)],
            clean=True
        )

def task_05_analyse():
    """Step 05: Plot subject ERP and extract peaks"""
    for subject in subjects:
        yield dict(
            name=subject,
            targets=[fname.evokedFrequent(subject=subject), fname.evokedRare(subject=subject), fname.epochs(subject=subject)],
            actions=["python 05_analyse.py {sub}".format(sub=subject)],
            file_dep=[fname.reference(subject=subject)],
            clean=True
        )

def task_06_grandAverage():
    """Step 06: Plot grand average"""
    return dict(
            targets=[fname.totalReport],
            actions=["python 06_grandAverage.py {sub}".format(sub= ' '.join([subject for subject in subjects]))],
            file_dep=[fname.evokedFrequent(subject=subject) for subject in subjects] + [fname.evokedRare(subject=subject) for subject in subjects]
        )