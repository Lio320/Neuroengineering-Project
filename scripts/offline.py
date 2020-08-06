import sys
import mne
import numpy as np
from matplotlib import pyplot as plt

from utils import add_parent
add_parent()
from sonify import offline
from sonify.offline import OfflineSonify


# Path to the vhdr file (brainvision)
dataset_folder = 'dataset/sub-05/eeg'
dataset_file = 'sub-05_task-matchingpennies_eeg.vhdr'

# Sampling frequency after downsampling
samp_freq = 200

if __name__ == "__main__":

    # Get raw file
    raw = offline.preprocess.get_raw()
    # raw.crop(0,50)

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

    #Filter the data to extract only EOG
    filter_array = mne.filter.filter_data(array, 200, 1, 10, fir_window='hann', filter_length="10s", fir_design='firwin2')

    #Compute mean, standard deviation and threshold for each channel
    mean, std, thr, thr2 = sonify.offline.artifact.compute_mean_std_trh(filter_array)

    #Extract artifacts and number, for each channel
    Nartifacts, artifacts = offline.artifact.find_artifacts(filter_array, thr, thr2)

    #Plot artifacts
    offline.artifact.plot_artifacts_ch(artifacts, thr, thr2)

    # AIM 1.B
    raw.plot(block=True)
    mu = raw.copy().filter(8, 13)
    mu.plot(block=True)

    #Convert mu rithm in array
    mu_array = mu._data
    mu_array = np.square(mu_array)

    # Plot the mu rithm
    offline.artifact.plot_mu(mu_array)

    # Extract events
    events = mne.events_from_annotations(mu, {'Stimulus/S1': 1, 'Stimulus/S2': 2})
    event_dict = {'Stimulus/S1': 1,
                  'Stimulus/S2': 2}
    epochs = mne.Epochs(mu, events[0], tmin=-1, tmax=4, event_id=event_dict,
                        preload=True)

    # Evoked - Stimulus 1
    evoked = epochs['Stimulus/S1'].average()
    evoked.plot() # CP5 best

    # Evoked - Stimulus 2
    evoked2 = epochs['Stimulus/S2'].average()
    evoked2.plot() # CP6 best
    # END AIM 1.B

    ###### Sonification ######
    recording_length = len(artifacts[0]) / samp_freq
    sonification = OfflineSonify(recording_length, samp_freq)

    ###### Sonify eog artifacts ######
    eog_sonification = sonification.sonify_eog_artifacts(artifacts)
    sonification.write_data_to_wav("./media/eog_artifacts_ch_FC5.wav", eog_sonification)

    ###### Sonify mu rhythm ######
    mu_sonification = sonification.sonify_mu_rhythm(mu_array)
    sonification.write_data_to_wav("./media/mu_rhythm_ch_CP5.wav", mu_sonification)

    ###### Sonify all together ######
    final_sonification = sonification.data_unification(eog_sonification, mu_sonification)
    sonification.write_data_to_wav("./media/final_ch_FC5_CP5.wav", final_sonification)

