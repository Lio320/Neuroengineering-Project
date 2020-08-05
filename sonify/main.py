import preprocess
import artifact_detection
import options

import mne
import numpy as np
from matplotlib import pyplot as plt
from scipy.io.wavfile import write

# Get raw file
raw = preprocess.get_raw()
# raw.crop(0,100)
# width = len(raw._data[0])
# raw.crop(0, 1)

# Print info about the raw data
print(raw)
print(raw.info)

# Plot PSD
# raw.plot_psd()
# Plot DATA
# raw.plot(block=True)


# Aim 1.a
#Extract the ndarray from raw
array = raw._data
# array = np.pad(array, [(0,0),(0,10000)])

#Filter the data to extract only EOG
filter_array = mne.filter.filter_data(array, 200, 1, 10,fir_window='hann', filter_length="10s", fir_design='firwin2')

#Compute mean, standard deviation and threshold for each channel
mean1, std1, thr1 = artifact_detection.compute_mean_std_trh(filter_array)

#Extract artifacts and number, for each channel
Nartifacts, artifacts = artifact_detection.find_artifacts(filter_array, thr1)

#Build the time line, 3739340 is 10 times the duration of one channel
f = options.samp_freq #Frequency 200 Hz
Time = np.arange(0, len(array[0])/f, 1/f)

artifact_detection.plot_artifacts_ch(Time, artifacts, thr1)


"""
plt.figure()
plt.subplot(2,1,1)
plt.plot(Time, array[1])
plt.ylim((-0.0002, 0.0002))
plt.xlim((0, 10))
plt.subplot(2,1,2)
plt.plot(Time, filter_array[1])
plt.ylim((-0.0002, 0.0002))
plt.xlim((0, 10))
plt.show()
"""

# AIM 1.B
""" raw.plot(block=True)
mu = raw.copy().filter(8, 13)
mu.plot(block=True)

events = mne.events_from_annotations(mu, {'Stimulus/S1': 1, 'Stimulus/S2': 2})
event_dict = {'Stimulus/S1': 1,
              'Stimulus/S2': 2}
epochs = mne.Epochs(mu, events[0], tmin=-1, tmax=4, event_id=event_dict,
                    preload=True)

# CP5 best
evoked = epochs['Stimulus/S1'].average()
evoked.plot()

# CP6 best
evoked2 = epochs['Stimulus/S2'].average()
evoked2.plot() """

""" # Sonify
pick_ch_CP5 = mu.copy().pick_channels(['CP5'])
pick_ch_CP6 = mu.copy().pick_channels(['CP6'])

data = pick_ch_CP5._data[0]
data = np.int16(data/np.max(np.abs(data)) * 65535)
print(data)
write('test.wav', 200, data) """
# END AIM 1.B


###### Sonify eog artifacts ######
samplerate = 44100
fs = 440 # A note
maxTime = len(artifacts[0])/options.samp_freq # Time of the recording
numSamples = int(np.ceil(maxTime*samplerate)) # Number of samples in order to have maxTime and samplerate
t = np.linspace(0., maxTime, numSamples)
# print(int(np.ceil(maxTime*samplerate)))
# print(len(artifacts[0]))
scale = np.iinfo(np.int16).max # Scale needed for wav
data = np.sin(2. * np.pi * fs * t)

# Produce a sound after every blink
coeff = np.zeros(numSamples)
samp_freq_conversion = int(np.ceil(samplerate / options.samp_freq))
duration =  int(0.2 * options.samp_freq) # where options.samp_freq is 1 sec
i = 0
for samp in artifacts[0]:
    if samp != 0:
        for j in range(i*samp_freq_conversion, (i+duration)*samp_freq_conversion): 
            if j < numSamples:
                coeff[j] = 1
    print(i, ' out of ', len(artifacts[0]))
    i += 1
print(i, ' out of ', len(artifacts[0]))
data = data * coeff

data = np.int16(data/np.max(np.abs(data)) * scale) # apply scale and convert to int16
write("eog_artifacts_ch_FC5.wav", samplerate, data)
############
