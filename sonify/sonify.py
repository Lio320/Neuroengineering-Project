import numpy as np
import warnings
import sounddevice as sd
from scipy.io.wavfile import read, write

class Sonify():
    """Artifact detection and sonification
    Args:
        detector: detector object
            Instantiated artifact detector class.
            For available options refer to sonify.artifact.py
        stream_sr: int
            Sampling rate of the EEG recording
        file_path: str
            Path to the resulting .wav recoring
    """
    def __init__(self, detector, stream_sr, file_path=None):
        self.parent = detector 
        self.audio_sr = 44100 # Hz
        self.note = 440 # A4
        self.fs = int(stream_sr)
        self.warning = False
        self.file_path = file_path
        if file_path and ".wav" not in file_path:
            self.file_path += ".wav"

    def insert(self, ts, stream):
        ts_detect = self.parent.insert(ts, stream)
        duration = len(ts) / self.fs
        if ts_detect and not self.warning:
            if duration < 0.1:
                warnings.warn("Consider increasing the pull interval" + \
                " since the audio is pratically inaudible", Warning)
                self.warning = True

        if ts_detect:
            t = np.arange(int(duration * self.audio_sr))
            signal = np.sin(self.note * t)
            mask = _gaussian_window(len(signal), 3000)
            output = signal*mask / 2
            sd.play(output, self.audio_sr)
        else:
            output = np.zeros(int(duration*self.audio_sr))

        if self.file_path:
            try:
                _, sound = read(self.file_path)
                sound = np.append(sound, output)

            except FileNotFoundError:
                sound = output

            write(self.file_path, self.audio_sr, sound.astype(np.float32))

        return ts_detect


def _gaussian_window(points, sig):
    
    n = np.arange(0, points) - (points - 1.0) / 2.0
    window = np.exp(-0.5 * np.abs(n / sig)**2)
    return window
