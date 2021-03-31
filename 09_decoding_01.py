from config import config, fname, n_jobs
from utils import *
import sklearn.pipeline
import sklearn.linear_model
import sklearn.model_selection
import warnings
from sklearn.exceptions import ConvergenceWarning
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import os

subject = handleSubjectArg()

'''calculate binary labels for condition differences'''
def getEpochLabels(epochs):
    inverse_dict = {value: key for key, value in epochs.event_id.items()}

    event_keys = epochs.events[:,2]
    events_condition = [inverse_dict[key].split("/")[0] for key in event_keys]

    # Change to binary labels: condition1 == 0 and condition2 == 1
    labels_binary = []
    for cond in events_condition:
        labels_binary.append(1 if cond == "cond2" else 0)
    return np.array(labels_binary)

'''show decoding plot for given model'''
def plotData(x, y, model_type, t_max):
    fig, ax = plt.subplots(constrained_layout=True, figsize=(16, 9))
    ax.plot(x, y, label="score")
    ax.set_xlabel("Time in s")
    ax.set_ylabel("Score: "+config["decode_scoring"])
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1.0])
    ax.set_title(model_type +" scores")
    ax.axhline(0.5, color="r", linestyle='--', label="random")
    ax.legend()
    ax.grid(alpha=0.25)
    ax.set_axisbelow(True)
    ax.xaxis.set_major_locator(MultipleLocator(0.1))
    #ax.axvline(x=t_max, color="r", label="peak")
    return fig


epochs = mne.read_epochs(fname.epochs(subject=subject))

#equalize event_counts for decoding to have same signal to noise ratio
#otherwise classifier would be biased to difference in condition occurences
epochs.equalize_event_counts(["cond1", "cond2"])

epochs.resample(256) #resample, normally unneccessary as already done in ERPCORE
epochs = epochs[["cond1", "cond2"]]
epochs = epochs.crop(tmin=-0.1, tmax=1.0)
labels = getEpochLabels(epochs)

selected_models = config["decoding_models"]

decoding_types = {
    "LogisticRegression": 
        sklearn.pipeline.Pipeline([
            ("transform", mne.decoding.Vectorizer()),
            ("model", sklearn.linear_model.LogisticRegression(solver="lbfgs", max_iter=config["decode_maxiter"])),
            
        ]),
    "SVM":
        sklearn.pipeline.Pipeline([
            ("scaler", sklearn.preprocessing.StandardScaler()),
            ("model", sklearn.svm.LinearSVC(max_iter=config["decode_maxiter"]))
        ])
}

data = {}
pipeline_list = [decoding_types[model] for model in selected_models]

#ignore convergence warning, they are expected with max_iter set too low alternatively set max iterations higher
warnings.filterwarnings('ignore', r'.*ConvergenceWarning.*')

#iterate and fit all decoding models
for pipeline, model_type in zip(pipeline_list, selected_models):
    
    #generate train/test split
    cross_val = sklearn.model_selection.StratifiedShuffleSplit(10, test_size=0.3, random_state=7)
    estimator = mne.decoding.SlidingEstimator(pipeline, scoring=config["decode_scoring"], n_jobs=n_jobs)

    score = mne.decoding.cross_val_multiscore(estimator, epochs.get_data(), labels, cv=cross_val, n_jobs=n_jobs)
    score = np.array(np.mean(score, axis=0))
    time = epochs.times
    t_max_score = time[np.argmax(score)]

    data[model_type] = {"time": time, "score": score}
    fig = plotData(time, score, model_type, t_max_score)
    addFigure(subject, fig, "Decoding with model: {}".format(model_type), "Decoding")

writeData(fname.decodingAnalysis(subject=subject), data)