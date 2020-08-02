import time
import os
import sys
import argparse
from collections import defaultdict
import threading

# https://github.com/sccn/xdf/
from xdf import load_xdf

# pip install pylsl
from pylsl import StreamInfo, StreamOutlet, IRREGULAR_RATE, local_clock

sys.setcheckinterval(1)

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

# argparse to define the argument format and populate the help funfction
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''Replay a LSL Recording from an XDF file.
Example usage: python replay_lsl.py my_recording.xdf --loop''')

parser.add_argument("file_path", type=lambda x: is_valid_file(parser, x),
                    help="path to .xdf file")
parser.add_argument('-v', '--verbose', help='verbose output',
                    action='store_true')
parser.add_argument('-r', '--repeat', dest='repeat_times', action='store',
                    default=1, help='repeat the stream N times Will not guarentee time accuracy across streams (default: 1)')
parser.add_argument('-l', '--loop', dest='repeat_times', action='store_const',
                    const=0, default=1,
                    help='loop the stream for ever. Will not guarentee time accuracy across streams (Same as --repeat 0)')

args = parser.parse_args()

try:
    print('Attempting to load xdf data')
    #dejitter_timestamps doesn't work in fedora 26
    streams, header = load_xdf(args.file_path, dejitter_timestamps=True, synchronize_clocks=True)
except Exception as e:
    print('Exception ', e)
    sys.exit(1)

#Python2/3 compatible iteratable item
def get_items(dict_object):
    for key in dict_object:
        yield key, dict_object[key]

#Search the defaultdictonary and add to the xml structure
def add_to_node(cur_dict, node):
    for key,value in get_items(dict(cur_dict)):
        if isinstance(value[0], defaultdict):
            for itm in value:
                new_node = node.append_child(key)
                add_to_node(itm, new_node)
        else:
            node.append_child_value(key, value[0])

def lsl_stream(stream, delay):
    s_info = stream['info']

    # Copy the stream meta data
    if float(s_info['nominal_srate'][0]) < 0.00001:
        nominal_srate = IRREGULAR_RATE
    else:
        nominal_srate = float(s_info['nominal_srate'][0])

    # new stream info
    # trying to replicate the from s_info
    info = StreamInfo(s_info['name'][0],
                      s_info['type'][0],
                      int(s_info['channel_count'][0]),
                      nominal_srate,
                      s_info['channel_format'][0],
                      'LSL_REPLAY')
    
    if (s_info['desc'][0] is not None):
        add_to_node(s_info['desc'][0], info.desc())

    # Start the LSL stream
    print('Starting LSL stream: ' + s_info['name'][0])
    outlet = StreamOutlet(info, 1, 36)
    time.sleep(delay+10)

    first_timestamp = stream["time_stamps"][0]
    cur_timestamp = stream["time_stamps"][0]
    last_timestamp = first_timestamp
    
    first_clock = local_clock()
    clock_offset = first_timestamp - first_clock

    remaining_loops = int(args.repeat_times)
    time_offset = 0


    while (remaining_loops >= 1 or remaining_loops == 0):
        # Reduce by 1 if not infinite loop key (0)
        # special case for 1 so its not the infinite loop key
        if remaining_loops > 1:
            remaining_loops -= 1
        elif remaining_loops == 1:
            remaining_loops = -1

        for x in range(0, len(stream["time_stamps"])):
            cur_timestamp = stream["time_stamps"][x] + time_offset

            mysample = stream["time_series"][x]
            stamp = cur_timestamp - clock_offset

            if args.verbose:
                print(mysample)

            
            delta = stamp - local_clock()

            if delta > 0:
                time.sleep(delta)

            outlet.push_sample(mysample, stamp)

            last_timestamp = cur_timestamp
                
        print('end of stream')
            

        time_offset = cur_timestamp - first_timestamp
    print("Ending LSL stream: " + s_info['name'][0])


first_timestamp = streams[0]["time_stamps"][0]
for stream in streams:
    if len(stream["time_stamps"]) < 1:
        continue

    if stream["time_stamps"][0] < first_timestamp:
        first_timestamp = stream["time_stamps"][0]


threads = []
def has_live_threads(_threads):
    return True in [t.isAlive() for t in _threads]

for stream in streams:
    if len(stream["time_stamps"]) < 1:
        continue

    delay = stream["time_stamps"][0] - first_timestamp
    t = threading.Timer(0, lsl_stream, [stream, delay])
    t.daemon = True
    t.start()
    threads.append(t)

while has_live_threads(threads):
    for t in threads:
        t.join(10)