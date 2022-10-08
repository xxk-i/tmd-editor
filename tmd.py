import os
from re import L
import sys
from typing import Text
import ioUtils
import json

class Header:
    def __init__(self, file):
        self.MAGIC = ioUtils.read_int32(file)

class TextEntry:
    def __init__(self, file):
        self.length = ioUtils.read_int32(file)
        self.text = ""
        for i in range (self.length - 1):
            self.text += file.read(2).decode("utf-16le")
        self.terminator = file.read(1)
        self.padding = file.read(1)

class EventMessagePair:
    def __init__(self, file):
        self.event = TextEntry(file)
        self.message = TextEntry(file)

class TMD:
    def __init__(self, file, file_size):
        self.header = Header(file)
        self.pairs = [] 

        while (file.tell() < file_size):
            self.pairs.append(EventMessagePair(file))
    
    def write_string(file, text):
        ioUtils.write_Int32(file, len(text) + 1)    # length str with null termination
        file.write(text.encode("utf-16le"))   # text
        ioUtils.write_byte(file, 0x00)   # null terminator 
        ioUtils.write_byte(file, 0x00)   # padding

def json_to_tmd(in_file):
    file = open(in_file, "r")
    loaded_json_data = json.load(file)

    outfile = open(os.path.splitext(in_file)[0] + "_packed.tmd", "wb+")

    ioUtils.write_Int32(outfile, len(loaded_json_data))

    for event in loaded_json_data:
        TMD.write_string(outfile, event)
        TMD.write_string(outfile, loaded_json_data[event])
        print(f"Event: {event}\tMessage: {loaded_json_data[event]}")
     

def tmd_to_json(in_file):
    tmd = TMD(open(in_file, "rb"), os.stat(in_file).st_size)

    outfile = open(os.path.splitext(in_file)[0] + ".json", "w+")

    final_dict = {}
    for pair in tmd.pairs:
        final_dict[pair.event.text] = pair.message.text

    # outfile.write(json.dumps({ "event": pair.event.text, "message": pair.message.text }, indent=4))
    outfile.write(json.dumps(final_dict, indent=4))

if __name__ == "__main__":
    in_file = sys.argv[1]
    in_file_extension = os.path.splitext(in_file)[1]

    if in_file_extension == ".tmd":
        tmd_to_json(in_file)

    elif in_file_extension == ".json":
        json_to_tmd(in_file)

    else:
        print("File type not supported")