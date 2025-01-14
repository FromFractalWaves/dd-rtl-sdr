# src/ddrtlsdr/control_manager.py

import logging
import time
import threading
from typing import Optional

from .device_manager import SDRDevice
from .librtlsdr_wrapper import open_device, close_device

logger = logging.getLogger("ddrtlsdr.control_manager")


class DeviceControlManager:
    def __init__(self):
        self.open_handles = {}  # Cache of open device handles

    def open_handle(self, device: SDRDevice, timeout: int = 10):
        """
        Opens a device handle, with retry logic and timeout.

        Args:
            device (SDRDevice): The device to open.
            timeout (int): Timeout in seconds for opening the device.

        Returns:
            handle: The device handle.

        Raises:
            OSError: If the device cannot be opened within the timeout.
        """
        if device.serial in self.open_handles:
            logger.info(f"Device {device.serial} is already open.")
            return self.open_handles[device.serial]

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                handle = open_device(device.index)
                self.open_handles[device.serial] = handle
                logger.info(f"Device {device.serial} opened successfully.")
                return handle
            except OSError as e:
                logger.warning(f"Failed to open device {device.serial}: {e}. Retrying...")
                time.sleep(0.5)

        logger.error(f"Unable to open device {device.serial} within {timeout} seconds.")
        raise OSError(f"Unable to open device at index {device.index}")

    def close_handle(self, device: SDRDevice):
        """
        Closes a device handle and removes it from the cache.

        Args:
            device (SDRDevice): The device to close.
        """
        handle = self.open_handles.pop(device.serial, None)
        if handle:
            close_device(handle)
            logger.info(f"Device {device.serial} closed and removed from cache.")
        else:
            logger.warning(f"Device {device.serial} was not open.")
