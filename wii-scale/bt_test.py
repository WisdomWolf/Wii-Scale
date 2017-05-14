from bluetoothctl import Bluetoothctl
import time

b = Bluetoothctl()
b.start_scan()
time.sleep(10)
devices = b.get_available_devices()
print('Available Devices:')
for device in devices:
    print('\t{}'.format(device['name']))
    if 'nintendo' in device['name'].lower():
        print('Found Nintendo device: {} {}'.format(device['name'], device['mac_address']))
        b.pair(device['mac_address'])
        status = b.connect(device['mac_address'])
        print('Connected: {}'.format(status))
        break
print(b.get_paired_devices())