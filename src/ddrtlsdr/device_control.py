# src/ddrtlsdr/device_control.py

import logging
import threading
import ctypes
from typing import Callable, Optional

from .device_manager import DeviceManager, SDRDevice
from .librtlsdr_wrapper import (
    open_device,
    close_device,
    set_center_freq,
    get_center_freq,
    set_sample_rate,
    get_sample_rate,
    set_gain,
    get_gain,
    read_async,
    cancel_async,
)
from .models import SDRConfig
from .logging_config import setup_logging

# Initialize centralized logging
setup_logging()
logger = logging.getLogger("ddrtlsdr.device_control")

class SDRStream:
    def __init__(self, device_handle, buffer_size: int = 16 * 16384, callback: Optional[Callable[[bytes], None]] = None):
        self.device_handle = device_handle
        self.buffer_size = buffer_size
        self.callback = callback
        self.running = False
        self.thread = None
        self.c_callback = None  # Ensure callback remains referenced

    def _c_callback(self, buf, length, ctx):
        if self.callback:
            data = ctypes.string_at(buf, length)
            self.callback(data)

    def _stream_thread(self):
        CALLBACK_FUNC = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_uint8), ctypes.c_int, ctypes.py_object)
        self.c_callback = CALLBACK_FUNC(self._c_callback)
        logger.debug("Starting asynchronous read.")
        read_async(
            self.device_handle,
            self.c_callback,
            None,
            1,  # Realtime flag
            self.buffer_size
        )
        logger.debug("Asynchronous read ended.")

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._stream_thread, daemon=True)
            self.thread.start()
            logger.info("Stream started.")

    def stop(self):
        if self.running:
            cancel_async(self.device_handle)
            self.thread.join()
            self.running = False
            logger.info("Stream stopped.")

class DeviceControl:
    def __init__(self):
        self.manager = DeviceManager()
        self.manager.initialize_devices()
        self.streams = {}  # Maps device serial to SDRStream
        self.open_handles = {}  # Cache of open device handles

    def open_device_cached(self, device: SDRDevice):
        if device.serial not in self.open_handles:
            handle = open_device(device.index)
            self.open_handles[device.serial] = handle
            logger.info(f"Device {device.serial} opened and cached.")
        return self.open_handles[device.serial]

    def close_device_cached(self, device: SDRDevice):
        handle = self.open_handles.pop(device.serial, None)
        if handle:
            close_device(handle)
            logger.info(f"Device {device.serial} closed and removed from cache.")

    def set_center_frequency(self, device: SDRDevice, freq_hz: int):
        handle = self.open_device_cached(device)
        set_center_freq(handle, freq_hz)
        logger.info(f"Set center frequency to {freq_hz} Hz for device {device.serial}.")

    def get_center_frequency(self, device: SDRDevice) -> int:
        handle = self.open_device_cached(device)
        freq = get_center_freq(handle)
        logger.info(f"Current center frequency for device {device.serial}: {freq} Hz.")
        return freq

    def set_sample_rate(self, device: SDRDevice, sample_rate_hz: int):
        handle = self.open_device_cached(device)
        set_sample_rate(handle, sample_rate_hz)
        logger.info(f"Set sample rate to {sample_rate_hz} Hz for device {device.serial}.")

    def get_sample_rate(self, device: SDRDevice) -> int:
        handle = self.open_device_cached(device)
        rate = get_sample_rate(handle)
        logger.info(f"Current sample rate for device {device.serial}: {rate} Hz.")
        return rate

    def set_gain(self, device: SDRDevice, gain: int):
        handle = self.open_device_cached(device)
        set_gain(handle, gain)
        logger.info(f"Set gain to {gain} for device {device.serial}.")

    def get_gain(self, device: SDRDevice) -> int:
        handle = self.open_device_cached(device)
        gain = get_gain(handle)
        logger.info(f"Current gain for device {device.serial}: {gain}.")
        return gain

    def get_device_info(self, device: SDRDevice) -> dict:
        info = {
            "serial": device.serial,
            "manufacturer": device.manufacturer,
            "product": device.product,
            "name": device.name,
            "center_frequency": self.get_center_frequency(device),
            "sample_rate": self.get_sample_rate(device),
            "gain": self.get_gain(device),
        }
        return info

    def start_stream(self, device: SDRDevice, callback: Callable[[bytes], None], buffer_size: int = 16 * 16384):
        if device.serial in self.streams:
            logger.warning(f"Stream already running for device {device.serial}.")
            return

        handle = self.open_device_cached(device)
        stream = SDRStream(handle, buffer_size, callback)
        self.streams[device.serial] = stream
        stream.start()
        logger.info(f"Stream started for device {device.serial}.")

    def stop_stream(self, device: SDRDevice):
        stream = self.streams.get(device.serial)
        if not stream:
            logger.warning(f"No active stream for device {device.serial}.")
            return
        stream.stop()
        self.close_device_cached(device)
        del self.streams[device.serial]
        logger.info(f"Stream stopped for device {device.serial}.")
        
    # def set_direct_sampling(self, device: SDRDevice, enable: bool):
    #     handle = self.open_device_cached(device)
    #     # Assuming librtlsdr has a function to set direct sampling
    #     if enable:
    #         result = rtl.rtlsdr_set_direct_sampling(handle, 1)
    #     else:
    #         result = rtl.rtlsdr_set_direct_sampling(handle, 0)
    #     if result != 0:
    #         logger.error(f"Failed to {'enable' if enable else 'disable'} direct sampling. Error code: {result}")
    #         raise ValueError(f"Unable to {'enable' if enable else 'disable'} direct sampling")
    #     logger.info(f"Direct sampling {'enabled' if enable else 'disabled'} for device {device.serial}.")

    # needs wrapper^