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

subjects = handleSubjectArg(multiSub=True)


for start_time in np.arange(config["t_start"], config["t_end"], config["t_sample"]):
    time_lst += [start_time]
    time_lst_plt += [start_time, start_time + config["t_sample"]]
    data = []
    for subject in subjects:
        with open(fname.decodingAnalysis(subject=subject), "r") as json_file:
            json_data = json.load(json_file)
            json_data = json_data["StandardScaler-LogisticRegression"]
            times, scores = json_data["times"], json_data["scores"]
            time_idx = [i for i, x in enumerate(times) if x >= start_time and x < start_time + config["t_sample"]]
            score = np.mean(scores[time_idx[0]:time_idx[-1]+1])
            #peaks.append([peak["peak_time"], peak["peak_alt"]])
            data.append(score)
    score_mean += [np.mean(data)] #* 2  # plateaus for plotting
    #peaks = np.array(peaks)
    #plt.hist(peaks[:,0])
    #plt.hist(data)
    #plt.show()
    #mean_peak_time = np.mean(peaks[:,0])
    # Non-parametric cluster-level paired t-test
    # The first dimension should correspond to the difference between paired samples (observations) in two conditions.
    # https://mne.tools/dev/generated/mne.stats.permutation_cluster_1samp_test.html
    alpha = 0.025
    statistics, pvalue = scipy.stats.ttest_1samp(data, 0.5, alternative='greater')
    pvalues.append(pvalue)
    # Calculate effect size with Cohan's d
    cohensds.append((np.mean(data) - 0.5) / (np.sqrt((np.std(data) ** 2 + 0 ** 2) / 2)))

#word = "not "*(p_value >= alpha)
#print(f"Difference of ERP peak between face and car condition is {word}significant with alpha={alpha} and p-value={p_value}.")
#print(test_results)
pvalues = np.array(pvalues)
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, constrained_layout=True, gridspec_kw={'height_ratios': [4, 6, 1, 1]}, figsize=(14, 8))
ax1.plot(time_lst_plt, np.repeat(score_mean, 2), label="score")
ax1.axhline(y=0.5, color="lightcoral", linestyle='--', label="chance")  # Horizontal line indicating chance (50%)
ax1.set_xlabel("Time [s]")
ax1.set_ylabel("ROC AUC Score")
ax1.set_xlim([0.0, 1.0])
ax1.set_title(f"Average decoding score across time")
ax1.legend()
ax1.grid(linestyle="dashed")
ax1.set_axisbelow(True)
ax1.xaxis.set_major_locator(ticker.MultipleLocator(0.1))

ax2.plot(time_lst_plt, np.repeat(pvalues, 2)*100, label="P-values")
ax2.axhline(y=alpha*100, color="lightcoral", linestyle='--', label=f"alpha={alpha*100}%")  # Horizontal line indicating chance (50%)
ax2.set_xlabel("Time [s]")
ax2.set_ylabel("%")
ax2.set_xlim([0.0, 1.0])
ax2.set_ylim([0.0*100, 1.0*100])
ax2.set_title(f"P-value of t-test across time")
ax2.legend()
ax2.grid(linestyle="dashed")
ax2.set_axisbelow(True)
ax2.xaxis.set_major_locator(ticker.MultipleLocator(0.1))
ax2.yaxis.set_major_locator(ticker.MultipleLocator(0.05*100))

ax3.pcolormesh(time_lst, [0,1], [pvalues < alpha], cmap="RdYlGn")
ax3.set_xlabel("Time [s]")
ax3.set_xlim([0.0, 1.0])
ax3.yaxis.set_visible(False)
ax3.set_title(f"Significance of t-test across time")
ax3.xaxis.set_major_locator(ticker.MultipleLocator(0.1))

ax4.pcolormesh(time_lst, [0,1], [np.clip(cohensds, a_min=0, a_max=3)], cmap="RdYlGn")
ax4.set_xlabel("Time [s]")
ax4.set_xlim([0.0, 1.0])
ax4.yaxis.set_visible(False)
ax4.set_title(f"Qualitative overview of effect size (Cohen's d) across time, d_max={np.max(cohensds):.3}, min_clipped at 0")
ax4.xaxis.set_major_locator(ticker.MultipleLocator(0.1))

addFigure(None, fig, "Decoding Analysis overview", "Decoding", totalReport=True)