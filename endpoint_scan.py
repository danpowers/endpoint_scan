#!/usr/bin/python

import argparse
import socket
import csv

def parse_arguments():
    p = argparse.ArgumentParser()
    p.add_argument("-i", "--input", action="store", help="input file")
    p.add_argument("-o", "--output", action="store", help="output file")
    a = p.parse_args()

    if not a.input or not a.output:
        p.print_help()
        exit(0)

    return a

def scan(InputFile, OutputFile):
    with open(InputFile, 'rb') as inputfile:
        with open(OutputFile, 'wb') as outputfile:
            csvInputFileReader = csv.reader(inputfile, delimiter=',')
            csvOutputFileWriter = csv.writer(outputfile, delimiter=',')

            for index, entry in enumerate(csvInputFileReader):
                if index == 0:
                    csvOutputFileWriter.writerow(entry)
                    continue

                endpoint, uuid, hostname, port, last_use, _ = \
                    entry[0], entry[1], entry[2], entry[3], entry[4], entry[5:]

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)

                try:
                    s.connect((hostname, int(port)))
                    reply = s.recv(4096)
                    if not "GridFTP Server" in reply:
                        raise Exception("Unexpected GridFTP Banner")
                    print("Scan of " + hostname + ":" + port + " in " + endpoint + " successful.")
                    csvOutputFileWriter.writerow([endpoint, uuid, hostname, port, last_use, "success", "none"])
                except Exception as e:
                    print("Scan of " + hostname + ":" + port + " in " + endpoint + " failed: " + str(e))
                    csvOutputFileWriter.writerow([endpoint, uuid, hostname, port, last_use, "fail", e])

                try:
                    s.shutdown(socket.SHUT_RDWR)
                    s.close()
                except Exception as e:
                    pass

def main():
    args = parse_arguments()
    scan(args.input, args.output)

if __name__ == "__main__":
    main()
