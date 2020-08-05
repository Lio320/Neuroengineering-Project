from sonify.stream import receive
from sonify.artifact import EventArtifactDetector

if __name__ == "__main__":
    art = EventArtifactDetector(39990)
    receive(fn=art.insert)
