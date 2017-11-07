#!/usr/bin/python

import argparse
import socket
import csv

def parse_arguments():
    p = argparse.ArgumentParser()
    p.add_argument("-i", "--input", action="store", help="input file")
    a = p.parse_args()

    if not a.input:
        p.print_help()
        exit(0)

    return a

def scan(InputFile):
    with open(InputFile, 'rb') as inputfile:
        csvInputFileReader = csv.reader(inputfile, delimiter=',')

        for index, entry in enumerate(csvInputFileReader):
            if index == 0:
                continue

            endpoint, uuid, hostname, port, _ = entry

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.settimeout(5)

            try:
                s.connect((hostname, int(port)))
                try:
                    reply = s.recv(4096)
                    if not "GridFTP Server" in reply:
                        raise Exception("Unexpected GridFTP Banner")
                    print("Scan of " + hostname + ":" + port + " in " + endpoint + " successful.")
                except Exception as e:
                    raise e
            except Exception as e:
                print("Scan of " + hostname + ":" + port + " in " + endpoint + " failed: " + str(e))

            try:
                s.shutdown(socket.SHUT_RDWR)
                s.close()
            except Exception as e:
                pass

def main():
    args = parse_arguments()
    scan(args.input)

if __name__ == "__main__":
    main()
