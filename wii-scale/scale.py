#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import time
import select

import numpy
import xwiimote

import util
from bluetoothctl import Bluetoothctl

class RingBuffer():
    def __init__(self, length):
        self.length = length
        self.reset()
        self.filled = False

    def extend(self, x):
        x_index = (self.index + numpy.arange(x.size)) % self.data.size
        self.data[x_index] = x
        self.index = x_index[-1] + 1

        if self.filled == False and self.index == (self.length-1):
            self.filled = True

    def append(self, x):
        x_index = (self.index + 1) % self.data.size
        self.data[x_index] = x
        self.index = x_index

        if self.filled == False and self.index == (self.length-1):
            self.filled = True


    def get(self):
        idx = (self.index + numpy.arange(self.data.size)) %self.data.size
        return self.data[idx]

    def reset(self):
        self.data = numpy.zeros(self.length, dtype=numpy.int)
        self.index = 0


def dev_is_balanceboard(dev):
    time.sleep(2) # if we check the devtype to early it is reported as 'unknown' :(

    iface = xwiimote.iface(dev)
    return iface.get_devtype() == 'balanceboard'

def wait_for_balanceboard():
    print("Waiting for balanceboard to connect..")
    mon = xwiimote.monitor(True, False)
    dev = None
    global mac_address
    bt.start_scan()
    print('scanning...')
    connected = False

    while True:
        time.sleep(1)
        if not connected:
            devices = bt.get_available_devices()
            for device in devices:
                if 'nintendo' in device['name'].lower():
                    if device not in bt.get_paired_devices():
                        mac_address = device['mac_address']
                        bt.pair(mac_address)
                        connected = bt.connect(mac_address)
                        print('Connected: {}'.format(connected))
                        trusted = bt.trust(mac_address)
                        print('Trusted: {}'.format(trusted))
                        break
                    else:
                        connected = True
                        print('Already paired')
                        break
        
        mon.get_fd(True) # blocks
        connected = mon.poll()

        if connected == None:
            continue
        elif dev_is_balanceboard(connected):
            print("Found balanceboard:", connected)
            dev = connected
            break
        else:
            print("Found non-balanceboard device:", connected)
            print("Waiting..")

    return dev

def format_measurement(x):
    return "{0:.2f}".format(x / 100.0)

def print_bboard_measurements(*args):
    sm = format_measurement(sum(args))
    tl, tr, bl, br = map(format_measurement, args)

    print("┌","─" * 21, "┐", sep="")
    print("│"," " * 8, "{:>5}".format(sm)," " * 8, "│", sep="")
    print("├","─" * 10, "┬", "─" * 10, "┤", sep="")
    print("│{:^10}│{:^10}│".format(tl, tr))
    print("│"," " * 10, "│", " " * 10, "│", sep="")
    print("│"," " * 10, "│", " " * 10, "│", sep="")
    print("│{:^10}│{:^10}│".format(bl, br))
    print("└","─" * 10, "┴", "─" * 10, "┘", sep="")

    print()
    print()

def measurements(iface):
    p = select.epoll.fromfd(iface.get_fd())

    while True:
        p.poll() # blocks

        event = xwiimote.event()
        iface.dispatch(event)

        tl = event.get_abs(2)[0]
        tr = event.get_abs(0)[0]
        br = event.get_abs(3)[0]
        bl = event.get_abs(1)[0]
        #print('tl: {}, tr: {}, br: {}, bl: {}'.format(tl, tr, br, bl))

        yield (tl,tr,br,bl)

def average_mesurements(ms, max_stddev=55):
    global iteration

    last_measurements = RingBuffer(800)

    while True:
        weight = sum(ms.next())
        print('averaging iteration', iteration)
        print('weight:', weight)

        if weight < 1000:
            print('skipping...')
            continue
        else:
            iteration += 1

        last_measurements.append(weight)

        mean = numpy.mean(last_measurements.data)
        stddev = numpy.std(last_measurements.data)

        if stddev < max_stddev and last_measurements.filled:
            yield numpy.array((mean, stddev))

def main():
    global iteration
    global bt
    bt = Bluetoothctl()
    
    if len(sys.argv) == 2:
        device = sys.argv[1]
    else:
        device = wait_for_balanceboard()

    iface = xwiimote.iface(device)
    iface.open(xwiimote.IFACE_BALANCE_BOARD)

    iteration = 0
    
    try:
#        for m in measurements(iface):
#            print_bboard_measurements(*m)

        for kg, err in average_mesurements(measurements(iface)):
            print('iteration', iteration)
            pkg = "qme.seri.wiiweight.weight"
            perr = "qme.seri.wiiweight.err"
            
            print("{:.2f} +/- {:.2f}".format(kg/100.0, err/100.0))

            kg, err = (int(round(x, 0)) for x in (kg, err))

            for d, p in zip((kg, err), (pkg, perr)):
                print(d, p)
                util.submit(p, d)

            sys.exit(0)


    except KeyboardInterrupt:
        bt.disconnect(mac_address)
        # bt.remove(mac_address)
        print("\nBye!")
        

if __name__ == '__main__':
    main()
