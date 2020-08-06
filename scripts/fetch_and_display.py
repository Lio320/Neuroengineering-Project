import sonify
from sonify.artifact import EventArtifactDetector
from sonify.sonify import Sonify

if __name__ == "__main__":
    detector = EventArtifactDetector(2000)
    #sonificator = Sonify(detector, 200, "output")
    sonificator = Sonify(detector, 200)
    sonify.stream.fetch(update_interval=5, fn=sonificator.insert)
