from os import makedirs
from config import fname
from utils import handleSubjectArg

# Handle command line arguments
subject = handleSubjectArg()

#make directories for further procesing
makedirs(fname.reports_dir, exist_ok=True)
makedirs(fname.subject_dir(subject=subject), exist_ok=True)