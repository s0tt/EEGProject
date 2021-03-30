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

# Decoding analysis Decode the main contrast of the experiment across time
# RQ: When is information about the conditions in our data available?
# https://mne.tools/stable/auto_tutorials/machine-learning/plot_sensors_decoding.html


time_list = []
time_plt = []

subjects = handleSubjectArg(multiSub=True)

time_list = np.arange(0, 1.0, config["decode_sampling"])
score_time_array = np.array(np.zeros(shape=(len(subjects), len(time_list))))


for subject_idx, subject in enumerate(subjects):
    #load subject data from step 01
    subject_data = readData(fname.decodingAnalysis(subject=subject))
    subject_data_model = subject_data[config["model_total_score"]]

    subject_time = subject_data_model["time"]
    subject_score = subject_data_model["score"]

    
    for time_idx, time_point in enumerate(time_list):       
        #find data in time bins
        idx = [i for i, x in enumerate(subject_time) if x >= time_point  and x < time_point + config["decode_sampling"]]
        #calculate mean score of bins
        score = np.mean(subject_score[idx])
        score_time_array[subject_idx, time_idx] = score
        
pvalues = []
score_means = []
time_means = []

for time_idx, time_point in enumerate(time_list):
    #calculate mean over time bins
    subject_scores = score_time_array[:, time_idx]
    score_means.append(np.mean(subject_scores))

    #calculate p-values over time bins
    # Non-parametric cluster-level paired t-test
    # The first dimension should correspond to the difference between paired samples (observations) in two conditions.
    # https://mne.tools/dev/generated/mne.stats.permutation_cluster_1samp_test.html
    t_stats, p_value = scipy.stats.ttest_1samp(subject_scores, 0.5, alternative='greater')
    pvalues.append(p_value if p_value else nan)
    if time_idx == len(time_list)-1:
        time_means.append(time_point) #end at last timepoint
    else:
        time_means.append(np.mean([time_point, time_list[time_idx+1]]))


#plot data
fig, ax = plt.subplots(2, 1, constrained_layout=True, gridspec_kw={'height_ratios': [5, 5]}, figsize=(16, 9))

#plot scores
ax[0].plot(time_means, score_means, label="score")
ax[0].axhline(y=0.5, color="red", linestyle='--', label="random")  # Horizontal line indicating chance (50%)
ax[0].set_xlabel("Time [s]")
ax[0].set_ylabel("Score: "+config["decode_scoring"])
ax[0].set_xlim([0, 1])
ax[0].set_title(f"Mean decoding score over subjects")
ax[0].legend()
ax[0].grid(alpha=0.25)
ax[0].set_axisbelow(True)
ax[0].xaxis.set_major_locator(ticker.MultipleLocator(0.1))


#plot p-values
ax[1].plot(time_means, np.array(pvalues), label="P-values")
ax[1].axhline(y=config["decode_alpha"], linestyle='--', color="red",label="alpha")
ax[1].set_xlim([0, 1])
ax[1].set_ylim([0, 1])
ax[1].set_title(f"P-value over mean decoding score")
ax[1].set_xlabel("Time [s]")
ax[1].set_ylabel("p-values")
ax[1].legend()
ax[1].grid(alpha=0.25)
ax[1].set_axisbelow(True)
ax[1].xaxis.set_major_locator(ticker.MultipleLocator(0.05))
ax[1].yaxis.set_major_locator(ticker.MultipleLocator(0.1))

addFigure(None, fig, "Decoding Analysis overview", "Decoding", totalReport=True)