# src/ddrtlsdr/librtlsdr_wrapper.py

import ctypes
import ctypes.util
import logging

from .logging_config import setup_logging

# Initialize centralized logging
setup_logging()
logger = logging.getLogger("ddrtlsdr.librtlsdr_wrapper")

# Load librtlsdr
try:
    rtl = ctypes.cdll.LoadLibrary(ctypes.util.find_library("rtlsdr"))
    logger.info("Successfully loaded librtlsdr.")
except OSError as e:
    logger.error(f"Failed to load librtlsdr: {e}")
    raise

# Define librtlsdr functions and their signatures
rtl.rtlsdr_get_device_count.restype = ctypes.c_int

rtl.rtlsdr_open.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_uint]
rtl.rtlsdr_open.restype = ctypes.c_int

rtl.rtlsdr_close.argtypes = [ctypes.c_void_p]
rtl.rtlsdr_close.restype = None

rtl.rtlsdr_set_center_freq.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rtl.rtlsdr_set_center_freq.restype = ctypes.c_int

rtl.rtlsdr_get_center_freq.argtypes = [ctypes.c_void_p]
rtl.rtlsdr_get_center_freq.restype = ctypes.c_uint32

rtl.rtlsdr_set_sample_rate.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
rtl.rtlsdr_set_sample_rate.restype = ctypes.c_int

rtl.rtlsdr_get_sample_rate.argtypes = [ctypes.c_void_p]
rtl.rtlsdr_get_sample_rate.restype = ctypes.c_uint32

rtl.rtlsdr_set_tuner_gain.argtypes = [ctypes.c_void_p, ctypes.c_int]
rtl.rtlsdr_set_tuner_gain.restype = ctypes.c_int

rtl.rtlsdr_get_tuner_gain.argtypes = [ctypes.c_void_p]
rtl.rtlsdr_get_tuner_gain.restype = ctypes.c_int

rtl.rtlsdr_read_async.argtypes = [
    ctypes.c_void_p,
    ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_uint8), ctypes.c_int, ctypes.py_object),
    ctypes.py_object,
    ctypes.c_int,
    ctypes.c_int,
]
rtl.rtlsdr_read_async.restype = ctypes.c_int

rtl.rtlsdr_cancel_async.argtypes = [ctypes.c_void_p]
rtl.rtlsdr_cancel_async.restype = None

def get_device_count():
    count = rtl.rtlsdr_get_device_count()
    logger.debug(f"Number of RTL-SDR devices found: {count}")
    return count

def open_device(index):
    handle = ctypes.c_void_p()
    result = rtl.rtlsdr_open(ctypes.byref(handle), index)
    if result != 0:
        logger.error(f"Failed to open device at index {index}. Error code: {result}")
        raise IOError(f"Unable to open device at index {index}")
    logger.info(f"Device at index {index} opened successfully.")
    return handle

def close_device(handle):
    rtl.rtlsdr_close(handle)
    logger.info("Device closed successfully.")

def set_center_freq(handle, freq_hz):
    result = rtl.rtlsdr_set_center_freq(handle, freq_hz)
    if result != 0:
        logger.error(f"Failed to set center frequency to {freq_hz} Hz. Error code: {result}")
        raise ValueError(f"Unable to set center frequency to {freq_hz} Hz")
    logger.info(f"Center frequency set to {freq_hz} Hz.")

def get_center_freq(handle):
    freq = rtl.rtlsdr_get_center_freq(handle)
    logger.info(f"Current center frequency: {freq} Hz.")
    return freq

def set_sample_rate(handle, rate_hz):
    result = rtl.rtlsdr_set_sample_rate(handle, rate_hz)
    if result != 0:
        logger.error(f"Failed to set sample rate to {rate_hz} Hz. Error code: {result}")
        raise ValueError(f"Unable to set sample rate to {rate_hz} Hz")
    logger.info(f"Sample rate set to {rate_hz} Hz.")

def get_sample_rate(handle):
    rate = rtl.rtlsdr_get_sample_rate(handle)
    logger.info(f"Current sample rate: {rate} Hz.")
    return rate

def set_gain(handle, gain):
    result = rtl.rtlsdr_set_tuner_gain(handle, gain)
    if result != 0:
        logger.error(f"Failed to set gain to {gain}. Error code: {result}")
        raise ValueError(f"Unable to set gain to {gain}")
    logger.info(f"Gain set to {gain}.")

def get_gain(handle):
    gain = rtl.rtlsdr_get_tuner_gain(handle)
    logger.info(f"Current gain: {gain}.")
    return gain

def read_async(handle, callback, context, num_buffers, buffer_size):
    result = rtl.rtlsdr_read_async(handle, callback, context, num_buffers, buffer_size)
    if result != 0:
        logger.error(f"Failed to start async read. Error code: {result}")
        raise RuntimeError(f"Unable to start async read. Error code: {result}")
    logger.info("Asynchronous read started.")

def cancel_async(handle):
    rtl.rtlsdr_cancel_async(handle)
    logger.info("Asynchronous read canceled.")
