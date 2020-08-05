# adapted from: https://github.com/labstreaminglayer/liblsl-Python/blob/master/pylsl/examples/ReceiveAndPlot.py
import sys
import pylsl
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

from .plot import MarkerInlet, DataInlet, TimeAxisItem

def read_streams(streams, plot_duration, plt):
    inlets = list()
    for info in streams:
        if 'Markers' in info.type(): # Originally "=="
            if info.nominal_srate() != pylsl.IRREGULAR_RATE \
                    or info.channel_format() != pylsl.cf_string:
                print('Invalid marker stream ' + info.name())
            print('Adding marker inlet: ' + info.name())
            inlets.append(MarkerInlet(info, plot_duration))
        elif info.nominal_srate() != pylsl.IRREGULAR_RATE \
                and info.channel_format() != pylsl.cf_string:
            print('Adding data inlet: ' + info.name())
            inlets.append(DataInlet(info, plt, plot_duration))
        else:
            print('Don\'t know what to do with stream ' + info.name())
            print(info.type())

    return inlets

def fn(x,y): pass # helper function

def receive(plot_duration=8, update_interval=30, pull_interval=100, fn=fn):
    """
    Receive, preprocess and plot LSL recording
    Args:
    plot_duration: int
        how many seconds of data to show
    update_interval: int
        ms between screen updates
    pull_interval: int
        ms between each pull operation
    fn: function
        preprocessing function
    """

    # Create the pyqtgraph window
    pw = pg.plot(title='LSL Plot')
    plt = pw.getPlotItem()
    plt.setAxisItems = {'bottom': TimeAxisItem(orientation = 'bottom')}
    plt.enableAutoRange(x=False, y=True)

    # firstly resolve all streams that could be shown
    streams = pylsl.resolve_streams()
    inlets = read_streams(streams, plot_duration, plt)

    # iterate over found streams, creating specialized inlet objects that will
    # handle plotting the data

    def scroll():
        """Move the view so the data appears to scroll"""
        # We show data only up to a timepoint shortly before the current time
        # so new data doesn't suddenly appear in the middle of the plot
        fudge_factor = pull_interval * .002
        plot_time = pylsl.local_clock()
        pw.setXRange(plot_time - plot_duration + fudge_factor, plot_time - fudge_factor)

    def update():
        # Read data from the inlet. Use a timeout of 0.0 so we don't block GUI interaction.
        mintime = pylsl.local_clock() - plot_duration
        # call pull_and_plot for each inlet.
        # Special handling of inlet types (markers, continuous data) is done in
        # the different inlet classes.
        if inlets:
            for inlet in inlets:
                if isinstance(inlet, DataInlet):
                    try:
                        ts, window = inlet.pull_and_plot(mintime, plt)
                        detected = fn(ts, window)
                        if detected:
                            for t in detected:
                                plt.addItem(pg.InfiniteLine(t, angle=90, movable=False, label="Artifact"))

                    except (TypeError, ValueError):
                        continue

                elif isinstance(inlet, MarkerInlet):
                    inlet.pull_and_plot(mintime, plt)

    # create a timer that will move the view every update_interval ms
    update_timer = QtCore.QTimer()
    update_timer.timeout.connect(scroll)
    update_timer.start(update_interval)

    # create a timer that will pull and add new data occasionally
    pull_timer = QtCore.QTimer()
    pull_timer.timeout.connect(update)
    pull_timer.start(pull_interval)


    # Start Qt event loop unless running in interactive mode or using pyside.
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app = QtGui.QApplication.instance()
        sys.exit(app.exec_())
