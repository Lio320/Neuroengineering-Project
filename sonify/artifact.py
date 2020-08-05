import numpy as np
from collections import deque

class ArtifactDetector:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.buffer = deque(maxlen=buffer_size)

    def insert(self, ts, stream): 
        
        # detect artifacts in the new data segment
        ts_detected = self.detect(ts, stream.T)

        # add new data to the deque
        self.buffer.rotate(-len(ts))
        self.buffer.extend(stream.T.tolist())

        return ts_detected

    def detect(self, t, signal):
        pass

class EventArtifactDetector(ArtifactDetector):

    def detect(self, t, signal):
        if len(self.buffer) >= self.buffer_size:

            base = np.asarray(self.buffer)
            mean = np.mean(base, axis=0)
            std = np.std(base, ddof=1, axis=0)

            artifacts = np.zeros_like(signal.T)
            artifacts[signal.T > (mean + 2*std)[:, np.newaxis]] = 1
            artifacts[signal.T < (mean - 2*std)[:, np.newaxis]] = 1
            artifacts = artifacts.sum(axis=0)
            ts = t[artifacts>=1]
            # quick-fix to prevent artifact redudancy
            # since the windows are in ms, it should be no problem
            ts = np.median(ts, keepdims=True)

            return ts.tolist()
