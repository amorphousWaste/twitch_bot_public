"""System Utils."""

import psutil

UNIT_MAPPING = {
    'kb': 1,
    'mb': 1000,
    'gb': 1000000,
    'tb': 1000000000,
}


async def get_cpu_percentage() -> float:
    """Get the CPU percentage in use.

    Returns:
        (float): CPU percentage.
    """
    return psutil.cpu_percent()


async def get_number_of_processes() -> int:
    """Get the number of running processes.

    Return:
        (int): Number of running processes.
    """
    return len(psutil.pids())


async def get_cpu_count() -> int:
    """Get the CPU count.

    Returns:
        (int): Number of CPUs.
    """
    return psutil.cpu_count()


async def get_cpu_speed() -> int:
    """Get the CPU speed.

    Returns:
        (int): Maximum CPU frequency in MHz.
    """
    return psutil.cpu_freq().max


async def get_memory_info(unit: str = 'kb') -> dict:
    """Get the percentage of available RAM.

    Args:
        unit (str): Unit to return the temperature in.
            Accepted values are 'kb', 'mb', 'gb', and 'tb'
                (not case-sensative).
            Default is 'kb'.

    Returns:
        memory_dict (dict): Memory dictionary.
    """
    raw_memory_dict = psutil.virtual_memory()._asdict()

    conversion = UNIT_MAPPING.get(unit.lower(), 1)

    memory_dict = {
        'total': raw_memory_dict.get('total', 0) / conversion,
        'available': raw_memory_dict.get('available', 0) / conversion,
        'percent': raw_memory_dict.get('percent', 0),
        'used': raw_memory_dict.get('used', 0) / conversion,
        'free': raw_memory_dict.get('free', 0) / conversion,
        'active': raw_memory_dict.get('active', 0) / conversion,
        'inactive': raw_memory_dict.get('inactive', 0) / conversion,
    }

    return memory_dict


async def get_disk_space(mount: str = None, unit: str = 'kb') -> dict:
    """Get disk space.

    Args:
        mount (str): Mount point.
            If not given, the root will be used: '/' or 'C:'.
        unit (str): Unit to return the temperature in.
            Accepted values are 'kb', 'mb', 'gb', and 'tb'
                (not case-sensative).
            Default is 'kb'.

    Returns:
        disk_info (dict): Disk space dictionary.
    """
    if not mount and psutil.sys.platform == 'win32':
        mount = 'C:\\'
    else:
        mount = '/'

    # Ensure the given mount exists.
    if mount in [m.mountpoint for m in psutil.disk_partitions()]:
        raw_disk_info = psutil.disk_usage(mount)._asdict()
    else:
        raw_disk_info = {'total': 0, 'used': 0, 'free': 0, 'percent': 0}

    conversion = UNIT_MAPPING.get(unit.lower(), 1)

    disk_info = {
        'total': raw_disk_info.get('total', 0) / conversion,
        'used': raw_disk_info.get('used', 0) / conversion,
        'free': raw_disk_info.get('free', 0) / conversion,
        'percent': raw_disk_info.get('percent', 0),
    }

    return disk_info


async def get_cpu_temp(unit: str = 'C') -> float:
    """Get the CPU temperature.

    Note: This is currently available only for Raspberry Pi.
    Temperature is returned in Celcius.

    Args:
        unit (str): Unit to return the temperature in.
            Accepted values are 'C', 'F', and 'K' (not case-sensative).

    Returns:
        cpu_temp (float): Temperature value.
    """
    # Try to import the library for monitoring the Raspberry Pi
    try:
        import gpiozero  # noqa
    except Exception:
        return 0.0

    cpu_temp = gpiozero.CPUTemperature().temperature

    if unit.lower() == 'f':
        cpu_temp = (cpu_temp * 9 / 5) + 32
    elif unit.lower() == 'k':
        cpu_temp = cpu_temp + 273.15

    return cpu_temp


async def get_gpu_temp(unit: str = 'C') -> float:
    """Get the GPU temperature.

    Note: This is currently available only for Raspberry Pi.
    Temperature is returned in Celcius.

    Args:
        unit (str): Unit to return the temperature in.
            Accepted values are 'C', 'F', and 'K' (not case-sensative).

    Returns:
        gpu_temp (float): Temperature value.
    """
    import os
    import re
    import subprocess

    gpu_command_path = '/opt/vc/bin/vcgencmd'
    if not os.path.exists(gpu_command_path):
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
