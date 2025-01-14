import logging
import threading
import time
from typing import Optional

from .device_manager import SDRDevice
from .device_control import DeviceControl
from .librtlsdr_wrapper import open_device

logger = logging.getLogger("ddrtlsdr.control_manager")

class DeviceControlManager:
    def __init__(self):
        self.control = DeviceControl()
        self.lock = threading.Lock()

    def try_open_device(self, device: SDRDevice, timeout: int = 10):
        """
        Attempt to open a device, retrying for the specified timeout if necessary.

        Args:
            device (SDRDevice): The SDR device to open.
            timeout (int): The maximum time to wait (in seconds) for the device to open.

        Raises:
            OSError: If the device cannot be opened within the timeout period.
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            with self.lock:
                try:
                    # Check if the device is already open
                    if self.control.is_device_open(device):
                        logger.info(f"Device {device.serial} is already open.")
                        return

                    # Attempt to open the device
                    handle = open_device(device.index)
                    self.control.open_handles[device.serial] = handle
                    logger.info(f"Device {device.serial} opened successfully.")
                    return
                except OSError as e:
                    logger.warning(f"Attempt to open device {device.serial} failed: {e}")

            # Wait a bit before retrying
            time.sleep(1)

        # Raise error if unable to open the device within the timeout
        raise OSError(f"Unable to open device {device.serial} after {timeout} seconds.")

    def open_device_with_handling(self, device: SDRDevice):
        """
        Open a device with error handling and timeout.

        Args:
            device (SDRDevice): The SDR device to open.

        Returns:
            None

        Raises:
            OSError: If the device cannot be opened.
        """
        try:
            self.try_open_device(device)
        except OSError as e:
            logger.error(f"Failed to open device {device.serial}: {e}")
            raise

# Example usage
if __name__ == "__main__":
    manager = DeviceControlManager()

    # Mock device for demonstration
    mock_device = SDRDevice(index=0, name="MockDevice", serial="00000001", manufacturer="Mock", product="MockProduct")

    try:
        manager.open_device_with_handling(mock_device)
    except OSError as e:
        logger.error(f"Critical error: {e}")
