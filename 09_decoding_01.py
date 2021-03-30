from config import config, fname, n_jobs
from utils import *
import sklearn.pipeline
import sklearn
import sklearn.model_selection
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import itertools
import json
import numpy as np
import scipy
import matplotlib.pyplot as plt
from matplotlib import ticker
import os

# Decoding analysis Decode the main contrast of the experiment across time
# RQ: When is information about the conditions in our data available?
# https://mne.tools/stable/auto_tutorials/machine-learning/plot_sensors_decoding.html
pvalues = []
cohensds = []
score_mean = []
time_lst = []
time_lst_plt = []

subject = handleSubjectArg()

def getEpochLabels(epochs):
    # Assert uniqueness of dict values to allow inversion
    events_dict_inv = {value: key for key, value in epochs.event_id.items()}
    assert len(epochs.event_id) == len(events_dict_inv)

    event_labels = epochs.events[:,-1]
    labels = [events_dict_inv[key].split("/")[0] for key in event_labels]

    # Change to integer rerpresentation: condition1 == 0 and condition2 == 1
    labels = [int(label == "cond2") for label in labels]
    return np.array(labels)

def plotData(x, y, model_type, t_max):
    fig, ax = plt.subplots(constrained_layout=True, figsize=(16, 9))
    ax.plot(x, y, label="score")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Score: "+config["decode_scoring"])
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1.0])
    ax.set_title(model_type +" scores")
    ax.legend()
    ax.grid(alpha=0.25)
    ax.set_axisbelow(True)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(0.1))
    ax.axhline(0.5, color="r", linestyle='--', label="random")
    #ax.axvline(x=t_max, color="r", label="peak")
    return fig


epochs = mne.read_epochs(fname.epochs(subject=subject))
epochs.resample(256)
epochs = epochs[["cond1", "cond2"]]
epochs = epochs.crop(tmin=-0.1, tmax=1.0)
labels = getEpochLabels(epochs)

selected_models = config["decoding_models"]

decoding_types = {
    "LogisticRegression": 
        sklearn.pipeline.Pipeline([
            #("scaler", mne.decoding.Scaler(scalings='mean')),
            ("transform", mne.decoding.Vectorizer()),
            ("model", sklearn.linear_model.LogisticRegression(solver="lbfgs", max_iter=400)),
            
        ]),
    "SVM":
        sklearn.pipeline.Pipeline([
            ("scaler", sklearn.preprocessing.StandardScaler()), #mne.decoding.Scaler(scalings='mean')
            #("transform", mne.decoding.Vectorizer()),
            ("model", sklearn.svm.LinearSVC(max_iter=400))
        ])
}

#Note
#Using this class is different from directly applying sklearn.preprocessing.StandardScaler
#  or sklearn.preprocessing.RobustScaler offered by scikit-learn. These scale each classification feature, 
# e.g. each time point for each channel, with mean and standard deviation computed across epochs, whereas mne.decoding.
# Scaler scales each channel using mean and standard deviation computed across all of its time points and epochs.

data = {}
pipeline_list = [decoding_types[model] for model in selected_models]

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