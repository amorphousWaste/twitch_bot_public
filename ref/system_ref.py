"""Get system information from a Raspberry Pi."""

import gpiozero
import os
import re
import subprocess

from setup import LOG

UNIT_MAPPING = {
    'kb': 1,
    'mb': 1000,
    'gb': 1000000,
    'tb': 1000000000,
}


def get_memory_info(unit='kb'):
    """Get memory info.

    Default values are in kB.

    Args:
        unit (str): Unit to return the temperature in.
            Accepted values are 'kb', 'mb', 'gb', and 'tb'.
            Not case-sensative.

    Returns:
        meminfo (dict): Contents of the meminfo file in a dictionary.
    """
    meminfo_path = '/proc/meminfo'
    if not os.path.exists(meminfo_path):
        LOG.error(f'Unable to find {meminfo_path}')
        return {}

    with open(meminfo_path, 'r') as in_file:
        meminfo_file = in_file.read()

    conversion = UNIT_MAPPING.get(unit.lower(), 1)

    meminfo = {}

    for info in meminfo_file.strip().split('\n'):
        key, value, unit = info.split()
        meminfo[key] = float(value) / conversion

    return meminfo


def get_cpu_temp(unit='C'):
    """Get the CPU temperature.

    Temperature is returned in Celcius.

    Args:
        unit (str): Unit to return the temperature in.
            Accepted values are 'C', 'F', and 'K'.
            Not case-sensative.

    Returns:
        cpu_temp (float): Temperature value.
    """
    cpu_temp = gpiozero.CPUTemperature().temperature

    if unit.lower() == 'f':
        cpu_temp = (cpu_temp * 9 / 5) + 32
    elif unit.lower() == 'k':
        cpu_temp = cpu_temp + 273.15

    return cpu_temp


def get_gpu_temp(unit='C'):
    """Get the GPU temperature.

    Temperature is returned in Celcius.

    Args:
        unit (str): Unit to return the temperature in.
            Accepted values are 'C', 'F', and 'K'.
            Not case-sensative.

    Returns:
        gpu_temp (float): Temperature value.
    """
    gpu_command_path = '/opt/vc/bin/vcgencmd'
    if not os.path.exists(gpu_command_path):
        LOG.error(f'Unable to find {gpu_command_path}')
        return 0.0

    raw_gpu_temp = str(
        subprocess.check_output([gpu_command_path, 'measure_temp'])
    )

    gpu_temp = float(re.search(r'temp=(\d*\.\d*)', raw_gpu_temp).groups()[0])

    if unit.lower() == 'f':
        gpu_temp = (gpu_temp * 9 / 5) + 32
    elif unit.lower() == 'k':
        gpu_temp = gpu_temp + 273.15

    return gpu_temp


def get_number_of_processes():
    """Get the number of running processes.

    Return:
        (int): Number of running processes.
    """
    return len(str(subprocess.check_output(['ps', 'ax'])).split('\\n')[1:])


def get_uptime():
    """Get system uptime.

    Returns:
        (str): Uptime formatted.
    """
    cut_command_path = '/usr/bin/cut'
    uptime_path = '/proc/uptime'
    if not os.path.exists(cut_command_path) or not os.path.exists(uptime_path):
        LOG.error(f'Unable to find {cut_command_path} or {uptime_path}')
        return ''

    raw_uptime = float(
        subprocess.check_output([cut_command_path, '-d.', '-f1', uptime_path])
    )

    seconds = raw_uptime % 60
    minutes = raw_uptime / 60 % 60
    hours = raw_uptime / 3600 % 24
    days = raw_uptime / 86400

    return f'{days}:{hours}:{minutes}:{seconds}'


def get_disk_space(unit='kb'):
    """Get disk space.

    Disk space is returned in kB.

    Args:
        unit (str): Unit to return the temperature in.
            Accepted values are 'kb', 'mb', 'gb', and 'tb'.
            Not case-sensative.

    Returns:
        disk_space_dict: (dict): Disk space dictionary.
    """
    raw_disk_space = (
        str(subprocess.check_output(['df', '/'])).split('\\n')[1].split()
    )

    conversion = UNIT_MAPPING.get(unit.lower(), 1)

    filesystem = raw_disk_space[0]
    size = float(raw_disk_space[1]) / conversion
    used = float(raw_disk_space[2]) / conversion
    available = float(raw_disk_space[3]) / conversion
    percentage_used = int(raw_disk_space[4].rstrip('%'))
    mount = raw_disk_space[5]

    disk_space_dict = {
        'filesystem': filesystem,
        'size': size,
        'used': used,
        'available': available,
        'percentage_used': percentage_used,
        'mount': mount,
    }

    return disk_space_dict
