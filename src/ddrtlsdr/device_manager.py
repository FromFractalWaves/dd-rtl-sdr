# src/ddrtlsdr/device_manager.py

import json
import logging
import os
import ctypes
from typing import List

from .librtlsdr_wrapper import (
    rtl,  # Import the rtl library instance from the wrapper
    get_device_count,
    open_device,
    close_device
)
from .models import SDRDevice, SDRConfig
from .logging_config import setup_logging

# Initialize centralized logging
setup_logging()
logger = logging.getLogger("ddrtlsdr.device_manager")

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

class DeviceManager:
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self.config: SDRConfig = SDRConfig()
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            logger.info("Configuration file not found. Creating a new one.")
            self.config = SDRConfig()
            self.save_config()
        else:
            try:
                self.config = SDRConfig.load(self.config_file)
                logger.debug(f"Loaded {len(self.config.devices)} devices from config.")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                self.config = SDRConfig()
                self.save_config()

    def save_config(self):
        try:
            self.config.save(self.config_file)
            logger.debug("Configuration saved.")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def enumerate_devices(self) -> List[SDRDevice]:
        count = get_device_count()
        logger.info(f"Number of RTL-SDR devices found: {count}")
        discovered_devices = []
        for i in range(count):
            # Retrieve device name
            try:
                name_ptr = rtl.rtlsdr_get_device_name(i)
                name = name_ptr.decode("utf-8") if isinstance(name_ptr, bytes) else "Unknown"
            except Exception as e:
                logger.error(f"Failed to get device name for index {i}: {e}")
                name = "Unknown"

            # Prepare buffers for USB strings
            serial = ctypes.create_string_buffer(256)
            manufacturer = ctypes.create_string_buffer(256)
            product = ctypes.create_string_buffer(256)

            # Retrieve USB strings
            try:
                result = rtl.rtlsdr_get_device_usb_strings(i, manufacturer, product, serial)
                if result != 0:
                    raise IOError(f"Failed to retrieve USB strings for device {i}.")
            except Exception as e:
                logger.error(f"Failed to retrieve USB strings for device {i}: {e}")
                serial_value = manufacturer_value = product_value = "Unknown"
            else:
                serial_value = serial.value.decode("utf-8") if serial.value else "Unknown"
                manufacturer_value = manufacturer.value.decode("utf-8") if manufacturer.value else "Unknown"
                product_value = product.value.decode("utf-8") if product.value else "Unknown"

            # Create and validate SDRDevice
            try:
                device = SDRDevice(
                    index=i,
                    name=name,
                    serial=serial_value,
                    manufacturer=manufacturer_value,
                    product=product_value,
                )
                logger.debug(f"Enumerated Device: {device.json()}")
                discovered_devices.append(device)
            except ValueError as ve:
                logger.error(f"Validation failed for device {i}: {ve}")

        # Merge new devices with existing config
        existing_serials = {dev.serial for dev in self.config.devices}
        for device in discovered_devices:
            if device.serial not in existing_serials:
                self.config.devices.append(device)
                logger.info(f"New device {device.serial} added to configuration.")
            else:
                logger.debug(f"Device {device.serial} is already recognized.")
        self.save_config()
        return self.config.devices

    def add_device_if_unrecognized(self, device: SDRDevice):
        if not any(dev.serial == device.serial for dev in self.config.devices):
            logger.info(f"Unrecognized device found: {device.serial}. Adding to config.")
            self.config.devices.append(device)
            self.save_config()
        else:
            logger.debug(f"Device {device.serial} is already recognized.")

    def verify_device_accessibility(self, device: SDRDevice) -> bool:
        try:
            handle = open_device(device.index)
            logger.info(f"Device {device.serial} is accessible.")
            close_device(handle)
            return True
        except IOError as e:
            logger.error(f"Device {device.serial} is locked or inaccessible. Error: {e}")
            return False

    def log_device_info(self, device: SDRDevice):
        logger.info(
            f"Device {device.index}: {device.manufacturer} {device.product} "
            f"Serial: {device.serial}"
        )

    def initialize_devices(self):
        devices = self.enumerate_devices()
        for device in devices:
            self.add_device_if_unrecognized(device)
            accessible = self.verify_device_accessibility(device)
            self.log_device_info(device)
            if not accessible:
                logger.warning(
                    f"Device {device.serial} is not accessible and may be in use."
                )

if __name__ == "__main__":
    manager = DeviceManager()
    manager.initialize_devices()
