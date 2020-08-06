import time
import os
import sys
import argparse
import warnings
import threading

from collections import defaultdict
from pyxdf import load_xdf
from pylsl import StreamInfo, StreamOutlet, IRREGULAR_RATE, local_clock


sys.setswitchinterval(1)

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def has_live_threads(_threads):
    return True in [t.is_alive() for t in _threads]

def add_to_node(cur_dict, node):
    """Search the defaultdictonary and add to the xml structure"""
    for key, value in cur_dict.items():
        if isinstance(value[0], defaultdict):
            for itm in value:
                new_node = node.append_child(key)
                add_to_node(itm, new_node)
        else:
            node.append_child_value(key, value[0])

def lsl_stream(stream, delay, us_rate, repeat_times, verbose):

    s_info = stream["info"]

    # Copy the stream meta data
    if float(s_info["nominal_srate"][0]) < 0.00001:
        nominal_srate = IRREGULAR_RATE
    else:
        nominal_srate = float(s_info["nominal_srate"][0])

    if us_rate:
        if us_rate > 0:
            if us_rate > nominal_srate:
                    warnings.warn("Undersampling frequecy ({} Hz) greater".format(us_rate) + \
                        "than nominal sampling rate ({} Hz). Using original".format(nominal_srate),
                    Warning)
                    step = 1
            else:
                    step = int(nominal_srate // int(us_rate))
                    nominal_srate = int(us_rate)
        else:
            warnings.warn("Invalid undersampling frequency. Using original")
            step = 1
    else:
        step = 1

    # new stream info
    # trying to replicate the from s_info
    info = StreamInfo(s_info["name"][0],
                      s_info["type"][0],
                      int(s_info["channel_count"][0]),
                      nominal_srate,
                      s_info["channel_format"][0],
                      "LSL_REPLAY")
    
    if (s_info["desc"][0] is not None):
        add_to_node(s_info["desc"][0], info.desc())


    first_timestamp = stream["time_stamps"][0]
    cur_timestamp = stream["time_stamps"][0]
    last_timestamp = first_timestamp
    
    first_clock = local_clock()
    clock_offset = first_timestamp - first_clock

    remaining_loops = int(repeat_times)
    time_offset = 0

    # Start the LSL stream
    print("Starting LSL stream: " + s_info['name'][0])
    outlet = StreamOutlet(info, 1, 36)
    time.sleep(delay+5)

    while (remaining_loops >= 1 or remaining_loops == 0):
        # Reduce by 1 if not infinite loop key (0)
        # special case for 1 so its not the infinite loop key
        if remaining_loops > 1:
            remaining_loops -= 1
        elif remaining_loops == 1:
            remaining_loops = -1

        for x in range(0, len(stream["time_stamps"]), step):
            cur_timestamp = stream["time_stamps"][x] + time_offset

            mysample = stream["time_series"][x]
            stamp = cur_timestamp - clock_offset

            if verbose:
                print(mysample)
            
            delta = stamp - local_clock()

            if delta > 0:
                time.sleep(delta)

            outlet.push_sample(mysample, stamp)

            last_timestamp = cur_timestamp
                
        print("end of stream")
            

        time_offset = cur_timestamp - first_timestamp
    print("Ending LSL stream: " + s_info["name"][0])


def replay(file_path, us_rate, repeat, verbose):
    """Replay .xdf file as LSL recording session
    Args:
        file_path: str
            path to .xdf file
        us_rate: int
            Sampling rate (Hz) to undersample original recording.
            If None it will keep the original sampling frequency
        repeat: int
            Number of times to repeat the recording
        verbose: bool
            Verbosity mode
    """

    print("Attempting to load xdf data")
    streams, header = load_xdf(file_path, dejitter_timestamps=True, synchronize_clocks=True)

    first_timestamp = streams[0]["time_stamps"][0]
    threads = list()
    for stream in streams:
        if len(stream["time_stamps"]) < 1:
            continue

        if stream["time_stamps"][0] < first_timestamp:
            first_timestamp = stream["time_stamps"][0]

    for stream in streams:
        if len(stream["time_stamps"]) < 1:
            continue

        delay = stream["time_stamps"][0] - first_timestamp
        t = threading.Timer(0, lsl_stream, [stream, delay, us_rate, repeat, verbose])
        t.daemon = True
        t.start()
        threads.append(t)

    while has_live_threads(threads):
        for t in threads:
            t.join(10)
