from config import config, fname

#Pipeline can be executed in parallel with: doit -n [nr_threads] -P thread
#e.g. in my case: doit -n 8 -P thread

#set subjects to analyze with pipeline
all_subjects = [str(sub).zfill(3) for sub in range(1, 40+1)] #all subjects

#switch between config subjects and manual set subjects
#subjects = config["subjects_numbers"]
subjects = all_subjects

##Set: True if clean, else set: [] --> False is somehow not allowed by Pydoit, allows cleaning with cmd: doit clean
clean_mode = [] #true


def task_00_init():
    """Step 00: Init the system"""
    for subject in subjects:
        yield dict(
            name = subject,
            actions=["python 00_init.py {sub}".format(sub=subject)],
            targets=[fname.subject_dir(subject=subject)],
            uptodate=[True],
            clean=clean_mode
        )


def task_01_filter():
    """Step 01: Filter EEG data"""
    for subject in subjects:
        yield dict(
            name=subject,
            targets=[fname.filt(subject=subject,fmin=config["bandpass_fmin"], fmax=config["bandpass_fmax"]), 
                        fname.report_html(subject=subject), fname.report(subject=subject)],
            actions=["python 01_filtering.py {sub}".format(sub=subject)],
            uptodate=[True],
            clean=clean_mode
        )

def task_02_clean():
    """Step 02: clean data either manually or auto"""
    for subject in subjects:
        yield dict(
            name=subject,
            targets=[fname.cleaned(subject=subject)],
            actions=["python 02_cleaning.py {sub}".format(sub=subject)],
            file_dep=[fname.filt(subject=subject,fmin=config["bandpass_fmin"], fmax=config["bandpass_fmax"])],
            clean=clean_mode
        )

def task_03_ica():
    """Step 03: ICA analysis to identify bad components"""
    for subject in subjects:
        yield dict(
            name=subject,
            targets=[fname.ica(subject=subject)],
            actions=["python 03_ica.py {sub}".format(sub=subject)],
            file_dep=[fname.cleaned(subject=subject)],
            clean=clean_mode
        )

def task_04_reference():
    """Step 04: clean data either manually or auto"""
    for subject in subjects:
        yield dict(
            name=subject,
            targets=[fname.reference(subject=subject)],
            actions=["python 04_reference.py {sub}".format(sub=subject)],
            file_dep=[fname.ica(subject=subject)],
            clean=clean_mode
        )

def task_05_analyse():
    """Step 05: Plot subject ERP and extract peaks"""
    for subject in subjects:
        yield dict(
            name=subject,
            targets=[fname.epochs(subject=subject)],
            actions=["python 05_analyse.py {sub}".format(sub=subject)],
            file_dep=[fname.reference(subject=subject)],
            clean=clean_mode
        )

def task_06_grandAverage():
    """Step 06: Plot grand average and calculate ERP statistics"""
    return dict(
            targets=[fname.totalReport],
            actions=["python 06_grandAverage.py {sub}".format(sub= ' '.join([subject for subject in subjects]))],
            file_dep=[fname.epochs(subject=subject) for subject in subjects],
            clean=clean_mode
        )

def task_07_timeFrequencyAnalysis01():
    """Step 07: Time frequency analysis subject individual"""
    for subject in subjects:
        yield dict(
                name=subject,
                targets=[fname.tfAnalysis(subject=subject)],
                actions=["python 07_tfAnalysis_01.py {sub}".format(sub=subject)],
                file_dep=[fname.epochs(subject=subject)],
                clean=clean_mode
            )

def task_08_timeFrequencyAnalysis02():
    """Step 08: Time frequency analysis across subjects with average evoked/induced and statistics"""
    return dict(
            targets=[],
            actions=["python 08_tfAnalysis_02.py {sub}".format(sub= ' '.join([subject for subject in subjects]))],
            file_dep=[fname.tfAnalysis(subject=subject) for subject in subjects],
            clean=clean_mode
        )

def task_09_decodingAnalysis01():
    """Step 09: Decoding analysis subject individual"""
    for subject in subjects:
        yield dict(
                name=subject,
                targets=[fname.decodingAnalysis(subject=subject)],
                actions=["python 09_decoding_01.py {sub}".format(sub=subject)],
                file_dep=[fname.epochs(subject=subject)],
                clean=clean_mode
            )
def task_10_decodingAnalysis02():
    """Step 10: Decoding analysis across subject with statistics"""
    return dict(
            targets=[],
            actions=["python 10_decoding_02.py {sub}".format(sub= ' '.join([subject for subject in subjects]))],
            file_dep=[fname.decodingAnalysis(subject=subject) for subject in subjects],
            clean=clean_mode
        )