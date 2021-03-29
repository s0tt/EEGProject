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
    # Convert from evt_id to string, e.g. "faces/4"
    labels = [events_dict_inv[key].split("/")[0] for key in event_labels]

    # Change to integer rerpresentation: condition1 == 0 and condition2 == 1
    labels = [int(label == "cond2") for label in labels]
    return np.array(labels)

def plotData(ax, x, y, model_name, feature_space_name, peak_time, peak_score):
    ax.axhline(0.5, color="lightcoral", label="random")  # Horizontal line indicating chance (50%)
    ax.plot(x, y, label="score")
    ax.scatter(peak_time, peak_score, s=200, color='red', marker='x', linewidths=3)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("ROC_AUC")
    ax.set_xlim([0.0, 0.5])
    ax.set_ylim([0.3, 1.0])
    ax.set_title(f"{feature_space_name} - {model_name}")
    ax.legend()
    ax.grid(linestyle="dashed")
    ax.set_axisbelow(True)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(0.1))


if not os.path.exists(fname.decodingAnalysis(subject=subject)) and not config["isDialogeMode"]:
    epochs = mne.read_epochs(fname.epochs(subject=subject))
    # Only consider epochs with faces or cars condition for classification
    epochs = epochs[["cond1", "cond2"]]
    epochs = epochs.crop(tmin=-0.1, tmax=1.0)
    labels = getEpochLabels(epochs)


    models = (("LogisticRegression", sklearn.linear_model.LogisticRegression(solver="lbfgs", max_iter=500)),
                ("SVM", sklearn.svm.LinearSVC()),)

    feature_space = (("StandardScaler", sklearn.preprocessing.StandardScaler()),  # equals mne.decoding.Scaler(scalings='mean')
                        ("Vectorizer", mne.decoding.Vectorizer()),
    )
    fig, axs = plt.subplots(len(models), len(feature_space), constrained_layout=True, figsize=(16, 10))
    fig.suptitle("Decoding Analysis")
    peaks = {}
    for ax, ((model_name, model), (feature_space_name, feature_space)) in zip(axs.flatten(), itertools.product(models, feature_space)):
        pipe_simple = sklearn.pipeline.Pipeline([('feature_space', feature_space), ('model', model)])
        cv = sklearn.model_selection.StratifiedShuffleSplit(10, test_size=0.2, random_state=0)
        timeDecode = mne.decoding.SlidingEstimator(pipe_simple, scoring='roc_auc', n_jobs=n_jobs, verbose=True)
        scores = mne.decoding.cross_val_multiscore(timeDecode, epochs.get_data(), labels, cv=cv, n_jobs=n_jobs)
        scores = scores.mean(axis=0).tolist()
        times = epochs.times.tolist()
        peak_time = times[np.argmax(scores)]
        peak_score = np.max(scores)
        peaks[f"{feature_space_name}-{model_name}"] = {"times": times, "scores": scores}
        plotData(ax, times, scores, model_name, feature_space_name, peak_time, peak_score)

    addFigure(subject, fig, "Different decodings overview", "Decoding")

    with open(fname.decodingAnalysis(subject=subject), "w") as json_file:
            json.dump(peaks, json_file, indent=4)