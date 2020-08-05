import mne
import numpy as np
from matplotlib import pyplot as plt

def compute_mean_std_trh(channel):
    """Compute the mean, standard deviation and artifact threshold for the given channel
    Args:
    	channel: numpy array
    Returns:
    	mean: list
            rolling avg. of the channel
        std: list
            rolling std of the channel
        thr: list
            rolling threshold of the channel
    """
    mean = []
    std = []
    thr = []
    for i in range(len(channel)):
        a = np.mean(channel[i])
        b = np.std(channel[i])
        mean.append(a)
        std.append(b)
        thr.append(mean[i] + 2*std[i])
        #thr.append((np.max(channel[i])-np.min(channel[i]))/4)
    return mean, std, thr

def find_artifacts(channel, thr):
    """Find artifacts within a channel
    Args:
        channel: np array
            recorded data of the given channel
        thr: list
            rolling threshold for the given channel
    Returns:
        Nartifacts: int
            number of artifacts in channel
        artifacts: list
            nested lists containing the artifacts
    """
        
    artifacts = [[],[],[],[],[],[],[],[],[],[]]
    Nartifacts = 0
    for i in range(len(channel)):
        for j in range(len(channel[0])): #10 channels epochs
            if (channel[i][j] > thr[i]).any(): #values in the channels
                Nartifacts+=1
                artifacts[i].append(channel[i][j])
            elif (channel[i][j] < -thr[i]).any(): #values in the channels
                Nartifacts+=1
                artifacts[i].append(channel[i][j])
            else:
                artifacts[i].append(0)
                
    return Nartifacts, artifacts


def plot_artifacts_ch(time, artifacts, thr):
    """Plot artifacts in the given channel
    Args:
        time: list
            time instant for the recordings
        artifacts: list
            nested list of artifacts
        thr: list
            list of thresholds
    """
    channel = int(input("Enter the channel number you want to observe:"))
    plt.plot(time, artifacts[channel-1])
    thr = np.repeat(thr[channel-1], 373934)
    plt.plot(time, thr)
    plt.plot(time, -thr)
    plt.xlabel("Time")
    plt.ylabel("Voltage of artifacts")
    plt.title("artifacts channel %d" %channel)
    plt.show()

# def detect_eog_artifacts(raw):
#     ecg_events = mne.preprocessing.find_ecg_events(raw, ch_name='C4')
#     return ecg_events
