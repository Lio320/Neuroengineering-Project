import mne
f = mne.io.read_raw_brainvision("./dataset/eeg_matchingpennies/sub-05/eeg/sub-05_task-matchingpennies_eeg.vhdr")
f = f.set_montage(mne.channels.make_standard_montage("standard_1020"))
f.load_data()
f_200 = f.copy().resample(200, npad='auto')

