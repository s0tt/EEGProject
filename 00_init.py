from os import makedirs
from config import fname
import argparse

# Handle command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', metavar='sub###', help='The subject to process')
args = parser.parse_args()
subject = args.subject
print('Processing subject:', subject)

makedirs(fname.reports_dir, exist_ok=False)
makedirs(fname.subject_dir(subject=subject), exist_ok=True)