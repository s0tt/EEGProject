import fnames
import argparse
from os import makedirs
from config import *
import mne

class PipelineStep:
    def __init__(self):
        #parse argument as subject number
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('subject', metavar='sub###', help='The subject to process')
        args = parser.parse_args()
        self.subject = args.subject
        self.report = fnames.report(subject=self.subject)
        self.config = 

    def createDirs(self):
        makedirs(fname.reports_dir, exist_ok=True)
        makedirs(fname.subject_dir(subject=self.subject), exist_ok=True)

    def addFig(self, figure, caption: str, section: str):
        with mne.open_report(self.report) as report:
            report.add_figs_to_section(
                figs_before,
                captions=caption,
                section=section,
                replace=True
            )
            report.save(fname.report_html(subject=subject), overwrite=True,
                        open_browser=False)

    def getSubject(self):
        print(self.subject)

    

