import pytest

from src.ddrtlsdr.device_control import DeviceControl
from src.ddrtlsdr.models import SDRDevice

@pytest.fixture
def sdr_device_control():
    return DeviceControl()

@pytest.fixture
def sdr_device(sdr_device_control):
    # Assumes the device index 0 corresponds to a valid SDR device connected to the system
    devices = sdr_device_control.list_devices()
    if not devices:
        pytest.fail("No SDR devices available for testing.")
    return devices[0]

def test_set_center_frequency(sdr_device_control, sdr_device):
    freq_to_set = 105_000_000  # 105 MHz
    sdr_device_control.set_center_frequency(sdr_device, freq_to_set)
    freq = sdr_device_control.get_center_frequency(sdr_device)
    assert freq == freq_to_set, f"Expected frequency {freq_to_set}, got {freq}"

def test_get_center_frequency(sdr_device_control, sdr_device):
    freq = sdr_device_control.get_center_frequency(sdr_device)
    assert freq > 0, f"Expected a positive frequency, got {freq}"

def test_set_sample_rate(sdr_device_control, sdr_device):
    sample_rate_to_set = 2_500_000  # 2.5 MHz
    sdr_device_control.set_sample_rate(sdr_device, sample_rate_to_set)
    rate = sdr_device_control.get_sample_rate(sdr_device)
    assert rate == sample_rate_to_set, f"Expected sample rate {sample_rate_to_set}, got {rate}"

def test_get_sample_rate(sdr_device_control, sdr_device):
    rate = sdr_device_control.get_sample_rate(sdr_device)
    assert rate > 0, f"Expected a positive sample rate, got {rate}"

def test_set_gain(sdr_device_control, sdr_device):
    gain_to_set = 15  # Example gain value
    sdr_device_control.set_gain(sdr_device, gain_to_set)
    gain = sdr_device_control.get_gain(sdr_device)
    assert gain == gain_to_set, f"Expected gain {gain_to_set}, got {gain}"

def test_get_gain(sdr_device_control, sdr_device):
    gain = sdr_device_control.get_gain(sdr_device)
    assert gain >= 0, f"Expected a non-negative gain, got {gain}"

def test_start_and_stop_stream(sdr_device_control, sdr_device):
    callback_results = []

    def callback(data):
        callback_results.append(data)

    buffer_size = 16384

    try:
        sdr_device_control.start_stream(sdr_device, callback, buffer_size)
        # Allow the stream to run briefly to collect data
        import time
        time.sleep(1)  # Stream for 1 second
    finally:
        sdr_device_control.stop_stream(sdr_device)

    assert len(callback_results) > 0, "Stream did not produce any data."
