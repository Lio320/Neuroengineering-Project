import mne
import numpy as np
from matplotlib import pyplot as plt
from .options import *

# Compute mean for each epoch
def compute_mean_std_trh(channel):
    """
        Computes mean, standard deviation and threshold for each
        channel of the EEG signal.


        Args:
            channel:
                The array containing the EEG signal.
        Returns:
            Statistical properties of the signal, and the threshold
            computed through them, for each of the channel in the
            EEG signal.
    """
    mean = []
    std = []
    thr = []
    thr2 = []
    for i in range(len(channel)):
        a = np.mean(channel[i])
        b = np.std(channel[i])
        mean.append(a)
        std.append(b)
        thr.append(mean[i] + 2*std[i])
        thr2.append(mean[i] - 2*std[i])
        #thr.append((np.max(channel[i])-np.min(channel[i]))/4)
    return mean, std, thr, thr2

# Find artifacts in a channel
def find_artifacts(channel, thr, thr2):
    """
        Computes the artifacts and the number of artifacts of the
        EEG signal. 

        Args:
            channel:
                The array containing the EEG signal.
            thr:
                The array containing the thresholds of the EEG 
                signal.
        Returns:
            The array containing the artifacts for each channel
            and the total number of artifacts.
    """
    artifacts = [[],[],[],[],[],[],[],[],[],[]]
    Nartifacts = 0
    for i in range(len(channel)):
        for j in range(len(channel[0])): #10 channels epochs
            if (channel[i][j] > thr[i]).any(): #values in the channels
                Nartifacts+=1
                artifacts[i].append(channel[i][j])
            elif (channel[i][j] < thr2[i]).any(): #values in the channels
                Nartifacts+=1
                artifacts[i].append(channel[i][j])
            else:
                artifacts[i].append(0)
                
    return Nartifacts, artifacts

# Change the channel number to plot different channels
def plot_artifacts_ch(artifacts, thr, thr2):
    """
        Plot the artifacts of the EEG signal for a chosen
        channel of interest. Also the threshold is plotted,
        to give an idea of the intensity of the artifacts.
        Used for visual inspection purposes.

        Args:
            artifacts:
                The array containing the artifacts of the 
                EEG signal.
            thr:
                The array containing the thresholds of the EEG 
                signal.
        Returns:
            The plot of the artifacts and the threshold, for a
            chosen channel, is sufficient to change the number of
            the channel to observe another one.
    """
    channel = int(input("Enter the channel number for which you want to observe the EOG artifacts: \n 1 -> FC5,\n 2 -> FC1,\n \
3 -> C3,\n 4 -> CP5,\n 5 -> CP1,\n 6 -> FC2,\n 7 -> FC6,\n 8 -> C4,\n 9 -> CP2,\n 10 -> CP6\nInsert number:"))
    #Build the time line, 3739340 is 10 times the duration of one channel
    f = samp_freq #Frequency 200 Hz
    time = np.arange(0, len(artifacts[channel-1])/f, 1/f)
    plt.plot(time, artifacts[channel-1])
    thr = np.repeat(thr[channel-1], len(artifacts[channel-1]))
    thr2 = np.repeat(thr2[channel-1], len(artifacts[channel-1]))
    plt.plot(time, thr)
    plt.plot(time, thr2)
    plt.xlabel("Time")
    plt.ylabel("Voltage of artifacts")
    plt.title("artifacts channel %d" %channel)
    plt.show()

# def detect_eog_artifacts(raw):
#     ecg_events = mne.preprocessing.find_ecg_events(raw, ch_name='C4')
#     return ecg_events

def plot_mu(mu):
    """
        Plot the mu rhythm of the EEG signal of interest,
        for a chosen channel. Used for visual inspection
        purposes. 

        Args:
            mu:
                The mu rhythm of the EEG signal
        Returns:
            The plot of the mu rhythm of the EEG, for a
            chosen channel, is sufficient to change the number of
            the channel to observe another one.
    """
    channel = int(input("Enter the channel number for which you want to observe the mu rhythm : \n 1 -> FC5,\n 2 -> FC1,\n \
3 -> C3,\n 4 -> CP5,\n 5 -> CP1,\n 6 -> FC2,\n 7 -> FC6,\n 8 -> C4,\n 9 -> CP2,\n 10 -> CP6\nInsert number:"))
    f = samp_freq #Frequency 200 Hz
    time = np.arange(0, (len(mu[channel-1]))/f, 1/f)
    plt.plot(time,mu[channel-1])
    plt.xlabel("Time")
    plt.ylabel("Mu rhythm ")
    plt.title("Mu rhythm  channel %d" %channel)
    plt.show()
