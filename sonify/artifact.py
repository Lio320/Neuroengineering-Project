import numpy as np

class ArtifactDetector:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size

    def insert(self, ts, stream): 
        
        ts_detected = None
        if stream.any():

            # detect artifacts in the new data segment
            ts_detected = self.detect(ts, stream)

            # add new data to the deque
            if not hasattr(self, "buffer"):
                self.buffer = stream
            else:
                self.buffer = np.hstack((self.buffer, stream))[:, -self.buffer_size:]

        return ts_detected

    def detect(self, t, signal):
        pass


class EventArtifactDetector(ArtifactDetector):

    def detect(self, t, signal):

        if hasattr(self, "buffer") and self.buffer.shape[1] >= self.buffer_size:

            mean = np.mean(self.buffer, axis=1)
            std = np.std(self.buffer, ddof=1, axis=1)

            artifacts = np.zeros_like(signal)
            artifacts[signal > (mean + 4*std)[:, np.newaxis]] = 1
            artifacts[signal < (mean - 4*std)[:, np.newaxis]] = 1
            artifacts = artifacts.sum(axis=0)
            ts = t[artifacts>=1]

            # quick-fix to prevent artifact redudancy                                  
            # since the windows are in ms, it should be no problem                     
            if ts.any():                                                               
                #ts = [np.min(ts), np.max(ts)]                                          
                ts = [np.median(ts, keepdims=True)]

            return ts

