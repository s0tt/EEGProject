import argparse
import mne
import ccs_eeg_utils
from config import config, fname, n_jobs
from mne_bids import (BIDSPath, read_raw_bids)
from matplotlib import pyplot as plt
import matplotlib
from utils import handleSubjectArg, readRawFif, addFigure
import json, os
import numpy as np
import scipy.stats as stats

subjects = handleSubjectArg(multiSub=True)


peak_list = []
evoked_cond1_list = []
evoked_cond2_list = []

for subject in subjects:
    try:
        epoch = mne.read_epochs(fname.epochs(subject=subject))
        evoked_cond1_list.append(epoch["cond1"].average())
        evoked_cond2_list.append(epoch["cond2"].average())

        #get peaks
        difference_wave = mne.combine_evoked([epoch["cond1"].average(),epoch["cond2"].average()],weights=[1, -1])
        _,peak_latency,peak_amplitude = difference_wave.pick(config["pick"]).crop(tmin=config["peak_window"][0], tmax= config["peak_window"][1]).get_peak(return_amplitude=True)
        peak_list.append(peak_amplitude)

    except FileNotFoundError:
        print("Please run step 05 for all subject before computing the grand average")

cond1_average = mne.grand_average(evoked_cond1_list)
cond2_average = mne.grand_average(evoked_cond2_list)
difference_wave = mne.combine_evoked([cond1_average,
                                  cond2_average],
                                 weights=[1, -1])

cond1_name = config["event_names"]["cond1"]
cond2_name = config["event_names"]["cond2"]

average = {cond1_name: cond1_average, cond2_name: cond2_average, "difference": difference_wave}

fig_evokeds = mne.viz.plot_compare_evokeds(average, picks=config["pick"], truncate_yaxis=False, truncate_xaxis=False, show=True if config["isDialogeMode"] else False)

#plot topography for the ERP and conditions
all_times = np.arange(epoch.baseline[0], 0.9, 0.05) #plot from baseline in time
fig_topo_cond1= cond1_average.plot_topomap(all_times, ch_type=config["analyse_pick"], time_unit='s',
                    ncols=8, nrows='auto', show=False)
fig_topo_cond2 = cond2_average.plot_topomap(all_times, ch_type=config["analyse_pick"], time_unit='s',
                    ncols=8, nrows='auto', show=False)
fig_topo_diff = difference_wave.plot_topomap(all_times, ch_type=config["analyse_pick"], time_unit='s',
                    ncols=8, nrows='auto', show=False)


fig_joint = difference_wave.plot_joint(title="Average difference wave over subjects", show=False)

#data line fitted
fig_hist, ax_hist = plt.subplots()
ax_hist.title.set_text("Peak data fitted curve")
ax_hist.set_xlabel("Number of peaks")
ax_hist.set_ylabel("Peak Amplitude [V]")
(mean, sigma) = stats.norm.fit(np.array(peak_list))
n, bins, patches = ax_hist.hist(np.array(peak_list), 20,  alpha=0.15, orientation="horizontal")
y = stats.norm.pdf(bins, mean, sigma)
normed = y*(np.amax(n)/np.amax(y))
l = ax_hist.plot(normed, bins, 'royalblue', linewidth=2)


#RQ: On which ERP-peaks do we find major difference between the conditions
#statistically test with t-test
t_values, p_value = stats.ttest_1samp(peak_list, 0.0, alternative="greater")


result_str = "T-test: p-value {} {} {} alpha".format(p_value, ">=" if p_value > config["alpha"] else "<", config["alpha"])
print(result_str)
print("Statistically it is {} that the {} ERP is present given this data at {}".format("significant" if p_value < config["alpha"] else "unsignificant", config["task"], config["pick"]))
addFigure(None, fig_evokeds, "Evoked Plot ","Peak-Analysis", totalReport=True, comments=result_str)
addFigure(None, fig_topo_cond1, "Average Topography condition: {} at pick: {}".format(cond1_name, config["analyse_pick"]),"Peak-Analysis", totalReport=True)
addFigure(None, fig_topo_cond2, "Average Topography condition: {} at pick: {}".format(cond2_name, config["analyse_pick"]),"Peak-Analysis", totalReport=True)
addFigure(None, fig_topo_diff, "Average Topography difference at pick: {}".format(config["analyse_pick"]),"Peak-Analysis", totalReport=True)
addFigure(None, fig_hist, "Peak histogram","Peak-Analysis", totalReport=True)
addFigure(None, fig_joint, "Joint average difference wave","Peak-Analysis", totalReport=True)