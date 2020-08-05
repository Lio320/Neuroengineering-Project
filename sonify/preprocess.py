import os
import mne
import options

# Checks if the files have already been downsampled to the samp_freq specified
# in options.py then if this is the case loads it and returns the raw object,
# otherwise first downsamples, saves it to file and then returns the raw object
def get_raw():
    cwd = os.getcwd()
    filename = str(options.samp_freq) + '_Hz_' + str(os.path.splitext(options.dataset_file)[0])+'_raw.fif'
    file_path = os.path.join(cwd, 'downsampled_eeg', options.dataset_folder, filename)
    if(os.path.isfile(file_path)):
        print('Downsampled eeg file already existing. Loading...')
        return load_downsampled_raw()
    else:
        print('The files will first be downsampled to ', options.samp_freq, 'Hz')
        return downsample_to_file(load_raw())

# Load raw data from brainvision files
def load_raw():
    cwd = os.getcwd()
    file_path = os.path.join(cwd, options.dataset_folder, options.dataset_file)
    raw = mne.io.read_raw_brainvision(file_path, preload=True)
    return raw

# Downsample the raw data and return it
def downsample(raw):
    print('Original sampling rate:', raw.info['sfreq'], 'Hz')
    raw_downsampled = raw.copy().resample(options.samp_freq)
    print('New sampling rate:', raw_downsampled.info['sfreq'], 'Hz')
    return raw_downsampled

# Downsample the raw data, save it to a fif file and return the raw object
def downsample_to_file(raw):
    # Downsample
    raw_downsampled = downsample(raw)

    # Save to file
    cwd = os.getcwd()
    dir = os.path.join(cwd, 'downsampled_eeg', options.dataset_folder)
    if not os.path.exists(dir):
        os.makedirs(dir)
    filename = str(options.samp_freq) + '_Hz_' + str(os.path.splitext(options.dataset_file)[0])+'_raw.fif'
    dir = os.path.join(dir, filename)
    raw_downsampled.save(dir, overwrite=True)
    return raw_downsampled

# Load the raw data that has been downsampled (fif file)
def load_downsampled_raw():
    cwd = os.getcwd()
    filename = str(options.samp_freq) + '_Hz_' + str(os.path.splitext(options.dataset_file)[0])+'_raw.fif'
    file_path = os.path.join(cwd, 'downsampled_eeg', options.dataset_folder, filename)
    raw = mne.io.read_raw_fif(file_path, preload=True)
    return raw