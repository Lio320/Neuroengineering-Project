import numpy as np
from scipy.io.wavfile import write

class OfflineSonify:
    """
    A class used for the sonification process done offline.

    Attributes:
        recording_length: float
            The duration of the eeg which is also equal to the
            duration of the output sound file
        
        audio_sample_rate: int
            The sampling rate of the autput audio wav file
        
        time: np.linespace
            Used to create the sin function that will generate 
            the sound
        
        wav_scale: float
            A coefficient used to scale the data before creating
            the wav file

    Methods:
        sonify_eog_artifacts(artifacts)
            Creates sound data from the eog artifacts
    """

    def __init__(self, recording_length, eeg_sampling_frequency):
        """
        Gets and prints the spreadsheet's header columns

        Args:
            recording_length: float
                The duration of the eeg which is also equal to the
                duration of the output sound file
        """
        self.recording_length = recording_length
        self.eeg_sampling_frequency = eeg_sampling_frequency
        self.audio_sample_rate = 44100
        self.n_samples = int(np.ceil(self.recording_length*self.audio_sample_rate))
        self.time = np.linspace(0., self.recording_length, self.n_samples)
        self.wav_scale = np.iinfo(np.int16).max

    
    def sonify_eog_artifacts(self, artifacts):
        """
        Creates audio data from the artifacts array.

        Creates audio data from the given artifacts array.
        It will produce a sinwave at 440Hz for 0.2 sec after each
        EOG artifact.

        Args:
            artifacts:
                The array containing the artifacts as floats.
                A value equal to 0 indicates no artifact at
                that sample.
                A value different from 0 indicates that there
                is an eog artifact at that sample.

        Returns:
            array containing the audio data that can be
            then written to a wav file with the method 
            write_data_to_wav(file_name, data)
        """
        channel = int(input("Enter the channel number for which you want to do the EOG sonification: \n 1 -> FC5,\n 2 -> FC1,\n \
3 -> C3,\n 4 -> CP5,\n 5 -> CP1,\n 6 -> FC2,\n 7 -> FC6,\n 8 -> C4,\n 9 -> CP2,\n 10 -> CP6\nInsert number:"))
        fs = 440 # A4 note
        data = np.sin(2. * np.pi * fs * self.time)
        coeff = np.zeros(self.n_samples)
        samp_freq_conversion = int(np.ceil(self.audio_sample_rate / self.eeg_sampling_frequency))
        duration =  int(0.2 * self.eeg_sampling_frequency) # where self.eeg_sampling_frequency is 1 sec
        i = 0
        for samp in artifacts[channel-1]:
            if samp != 0:
                for j in range(i*samp_freq_conversion, (i+duration)*samp_freq_conversion): 
                    if j < self.n_samples:
                        coeff[j] = 1
            print('EOG artifacts sonification: ', i, ' out of ', len(artifacts[channel-1]))
            i += 1
        print('EOG artifacts sonification: ', i, ' out of ', len(artifacts[channel-1]))
        data = data * coeff
        return data


    def sonify_mu_rhythm(self, mu_rhythm):
        """
        Creates audio data from the mu rhythm.

        Creates audio data from the given mu_rhythm
        array that have been sampled at mu_samp_freq Hz.
        It will produce a continuous sinwave with a 
        frequency of 1000Hz that varies its intensity
        depending on the intensity of the mu rhythm.

        Args:
            mu_rhythm:
                The array containing the mu_rhythm array
            mu_samp_freq:
                The sampling frequency of the mu rhythm

        Returns:
            array containing the audio data that can be
            then written to a wav file with the method 
            write_data_to_wav(file_name, data)
        """
        channel = int(input("Enter the channel number for which you want to do the mu rhythm sonification: \n 1 -> FC5,\n 2 -> FC1,\n \
3 -> C3,\n 4 -> CP5,\n 5 -> CP1,\n 6 -> FC2,\n 7 -> FC6,\n 8 -> C4,\n 9 -> CP2,\n 10 -> CP6\nInsert number:"))
        fs = 659.25	 # E5 note
        data = np.sin(2. * np.pi * fs * self.time)
        coeff = np.zeros(self.n_samples)
        samp_freq_conversion = int(np.ceil(self.audio_sample_rate / self.eeg_sampling_frequency))
        i = 0
        for samp in mu_rhythm[channel-1]:
            for j in range(i*samp_freq_conversion, (i+1)*samp_freq_conversion): 
                if j < self.n_samples:
                    coeff[j] = 0.001 + samp*1e10
            print('Mu rhythm sonification: ', i, ' out of ', len(mu_rhythm[channel-1]))
            i += 1
        print('Mu rhythm sonification: ', i, ' out of ', len(mu_rhythm[channel-1]))
        data = data * coeff
        return data


    def data_unification(self, data1, data2):
        """
        Creates audio data from two pieces of audio data.

        Args:
            data1:
                The first piece of audio data
            data2:
                The second piece of audio data

        Returns:
            array containing unified the audio data that 
            can be then written to a wav file with the 
            method write_data_to_wav(file_name, data)
        """
        data = data1 + data2
        return data


    def write_data_to_wav(self, file_name: str, data):
        """
        Writes the data as audio in a wav file

        Args:
            file_name: string
                The name of the wav file
            data: 
                The data to be written as a wav file
        """
        # apply scale and convert to int16
        data = np.int16(data/np.max(np.abs(data)) * self.wav_scale)
        # write to file
        write(file_name, self.audio_sample_rate, data)
        print('Sound ', file_name, ' has been saved')


