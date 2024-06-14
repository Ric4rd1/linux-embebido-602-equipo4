import sys
import subprocess
import glob
import serial # libreria pyserial
import socket

def find_available_serial_ports() -> list[str]:
    if sys.platform.startswith('win'): # Computadora windows
        platform = 'win'
        ports =[f'COM{i}' for i in range(1, 256)]
    elif sys.platform.startswith('linux'): # Computadora Linux
        platform = 'linux'
        ports =glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'): # Mac
        platform = 'darwin'
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported Platform')
    result = []
    for port in ports:
        early_stop = True if platform == 'win' else False
        try:
            s= serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            if early_stop:
                break
            continue

    return result

def get_current_network_name() -> str:
    try:
        if sys.platform.startswith('win'):
            # Windows
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if 'SSID' in line:
                    return line.split(':')[1].strip()
        elif sys.platform.startswith('linux'):
            # Linux
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if line.startswith('yes'):
                    return line.split(':')[1].strip()
        elif sys.platform.startswith('darwin'):
            # macOS
            result = subprocess.run(
                ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I'],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if 'SSID' in line:
                    return line.split(':')[1].strip()
        else:
            raise EnvironmentError('Unsupported Platform')
    except Exception as e:
        print(f"An error occurred while trying to get the network name: {e}")
        return ''

    return 'Unknown'

def get_ip_address() -> str:
    try:
        # Use socket to get the hostname and then the IP address
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        print(f"An error occurred while trying to get the IP address: {e}")
        return 'Unknown'
