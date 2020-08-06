import argparse
from sonify.stream import replay, is_valid_file

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Replay a LSL Recording from an XDF file")

#parser.add_argument("file_path", type=lambda x: is_valid_file(parser, x),
#        help="path to .xdf file")
parser.add_argument("-v", "--verbose", action="store_true",
        help="verbose output",)
parser.add_argument("-r", "--repeat", dest="repeat_times", action="store", default=1, 
        help="repeat the stream N times Will not guarentee time accuracy across streams (default: 1)")
parser.add_argument("-u", "--undersample", type=int, dest="us_rate", action="store", default=0, 
        help="Frequency (Hz) to undersample recording, if None it keeps sampling frequency as is")

if __name__ == "__main__":
    args = parser.parse_args()

    file_path = "./dataset/sourcedata/sub-05/eeg/sub-05_task-matchingpennies_eeg.xdf"
    us_rate = 200
    #replay(args.file_path, args.us_rate, args.repeat_times, args.verbose)
    replay(file_path, us_rate, args.repeat_times, args.verbose)

