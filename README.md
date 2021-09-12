# EEGProject P300/P3 A visual oddball experiment

>The P300 (P3) wave is an event-related potential (ERP) component elicited in the process of decision making. It is considered to be an endogenous potential, as its occurrence links not to the physical attributes of a stimulus, but to a person's reaction to it. More specifically, the P300 is thought to reflect processes involved in stimulus evaluation or categorization.

>It is usually elicited using the oddball paradigm, in which low-probability target items are mixed with high-probability non-target (or "standard") items. When recorded by electroencephalography (EEG), it surfaces as a positive deflection in voltage with a latency (delay between stimulus and response) of roughly 250 to 500 ms.[3]
>
>The signal is typically measured most strongly by the electrodes covering the parietal lobe. The presence, magnitude, topography and timing of this signal are often used as metrics of cognitive function in decision-making processes. While the neural substrates of this ERP component still remain hazy, the reproducibility and ubiquity of this signal makes it a common choice for psychological tests in both the clinic and laboratory. 

cited from: https://en.wikipedia.org/wiki/P300_(neuroscience)

## Project Task
This project provides a full pipeline for processing and analysing EEG P3 data form the publicly available [ERP-Core]((https://doi.org/10.1016/j.neuroimage.2020.117465)) using [MNE-Python](https://mne.tools/stable/index.html).
The pipeline includes:
- Preprocessing (Filter, Cleaning, ICA, Rereferencing)
- Analysation
- Grand Average
- Time-Frequency analysis (Morlet-Wavelets)
- Decoding Analysis (Logistic Regression, SVMs)

## Data
Project data was form the ERP-Core active visual P3 oddball experiments. There the participants were shown the sequence of familiar letters (e.g. A, B) and at specific timepoints the oddball letter (e.g. D) was shown ![P3 Experiment](/doc/P3_Oddball.png)
During the experiment the EEG potential were measured using the
10-20-EEG System.\
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/International_10-20_system_for_EEG-MCN.png/220px-International_10-20_system_for_EEG-MCN.png" alt="drawing" width="150"/> 

## Results
The grand average analysis over all subjects:
![P3 Experiment](/doc/GrandAverage.png)
The qualitative analysis suggests a event-related potential peak at ~300ms. This is the first sign of the P300 result. Additional significance tests prove a significant peak at ~300ms.

![P3 Experiment](/doc/GrandAverageTopography.png)
The topography reveals the potentials location in the middle cortex around the Pz electrode which will be used for further analysis.

Analysations in the Time-Frequency domain reveal the following induced and evoked peaks over subjects:
![P3 Experiment](/doc/TimeFrequencyAnalysis.png)
A T-test was used to find significant potentials, which can be oberserved in the lower row.

Analysations via Decoding revealed the following results:
![P3 Experiment](/doc/DecodingSVM.png). In the lower row the significant time ranges can be observed via p-values.

For further details on the project please refere to the Report.pdf inside the repository.

