from bluetoothctl import Bluetoothctl

b = Bluetoothctl()

print(b.get_available_devices())