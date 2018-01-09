#!/usr/bin/python

from threading import Thread
from Queue import Queue
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

class LogWriter(Thread):
    def __init__(self,logger_queue,logfile):
        Thread.__init__(self)
        self.logger_queue = logger_queue
        self.logfile = logfile

    def run(self):
        with open(self.logfile, 'ab+') as outputfile:
            csvOutputFileWriter = csv.writer(outputfile, delimiter=',')
            while True:
                entry = self.logger_queue.get()
                if len(entry) == 7:
                    endpoint, uuid, hostname, port, last_use, res, err = entry
                    if res == "success":
                        print("Scan of " + hostname + ":" + port + " in " + endpoint + " successful.")
                    else:
                        print("Scan of " + hostname + ":" + port + " in " + endpoint + " failed: " + str(err))
                csvOutputFileWriter.writerow(entry)
                outputfile.flush()
                self.logger_queue.task_done()

class ScanNode(Thread):
    def __init__(self, node_queue, logger_queue):
        Thread.__init__(self)
        self.node_queue = node_queue
        self.logger_queue = logger_queue

    def run(self):
        while True:
            entry = self.node_queue.get()
            if len(entry) == 7:
                endpoint, uuid, hostname, port, last_use, _, _ = entry
            else:
                endpoint, uuid, hostname, port, last_use = entry

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)

            try:
                s.connect((hostname, int(port)))
                reply = s.recv(4096)
                if not "GridFTP Server" in reply:
                    raise Exception("Unexpected GridFTP Banner")
                self.logger_queue.put([endpoint, uuid, hostname, port, last_use, "success", "none"])
            except Exception as e:
                self.logger_queue.put([endpoint, uuid, hostname, port, last_use, "fail", e])

            try:
                s.shutdown(socket.SHUT_RDWR)
                s.close()
            except Exception as e:
                pass

            self.node_queue.task_done()

def scan_list(input_file, node_queue, logger_queue):

    with open(input_file, 'rb') as inputfile:
        csvInputFileReader = csv.reader(inputfile, delimiter=',')

        for index, entry in enumerate(csvInputFileReader):
            if index == 0:
                logger_queue.put(entry)
                continue

            node_queue.put(entry)

    for i in range(10):
        scan_node_thread = ScanNode(node_queue, logger_queue)
        scan_node_thread.setDaemon(True)
        scan_node_thread.start()

    node_queue.join()
    logger_queue.join()

def main():
    args = parse_arguments()
    logger_queue = Queue()
    node_queue = Queue()

    logger_thread = LogWriter(logger_queue, args.output)
    logger_thread.setDaemon(True)
    logger_thread.start()

    scan_list(args.input, node_queue, logger_queue)

if __name__ == "__main__":
    main()
