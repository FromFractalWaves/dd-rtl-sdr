# tests/test_device_control.py

import pytest
from unittest.mock import patch, MagicMock

from src.ddrtlsdr.device_control import DeviceControl, SDRStream
from src.ddrtlsdr.models import SDRDevice

@pytest.fixture
def mock_rtl(mocker):
    with patch('src.ddrtlsdr.device_control.rtl') as mock_rtl_lib:
        mock_rtl_lib.rtlsdr_open.return_value = 0
        mock_rtl_lib.rtlsdr_close.return_value = None
        mock_rtl_lib.rtlsdr_set_center_freq.return_value = 0
        mock_rtl_lib.rtlsdr_get_center_freq.return_value = 100000000  # 100 MHz
        mock_rtl_lib.rtlsdr_set_sample_rate.return_value = 0
        mock_rtl_lib.rtlsdr_get_sample_rate.return_value = 2000000  # 2 MHz
        mock_rtl_lib.rtlsdr_set_tuner_gain.return_value = 0
        mock_rtl_lib.rtlsdr_get_tuner_gain.return_value = 10
        mock_rtl_lib.rtlsdr_read_async.return_value = 0
        return mock_rtl_lib

@pytest.fixture
def device_control(mock_rtl, tmp_path):
    with patch('src.ddrtlsdr.device_control.DeviceManager') as mock_manager:
        mock_manager_instance = MagicMock()
        mock_manager_instance.initialize_devices.return_value = None
        mock_manager_instance.enumerate_devices.return_value = []
        mock_manager_instance.add_device_if_unrecognized.return_value = None
        mock_manager_instance.verify_device_accessibility.return_value = True
        mock_manager_instance.log_device_info.return_value = None
        mock_manager.return_value = mock_manager_instance

        return DeviceControl()

def test_set_center_frequency(device_control, mock_rtl):
    device = SDRDevice(
        index=0,
        name="Device1",
        serial="Serial1",
        manufacturer="Manufacturer1",
        product="Product1"
    )
    device_control.set_center_frequency(device, 105000000)  # 105 MHz
    mock_rtl.rtlsdr_set_center_freq.assert_called_with(MagicMock(), 105000000)

def test_get_center_frequency(device_control, mock_rtl):
    device = SDRDevice(
        index=0,
        name="Device1",
        serial="Serial1",
        manufacturer="Manufacturer1",
        product="Product1"
    )
    freq = device_control.get_center_frequency(device)
    assert freq == 100000000
    mock_rtl.rtlsdr_get_center_freq.assert_called_with(MagicMock())

def test_set_sample_rate(device_control, mock_rtl):
    device = SDRDevice(
        index=0,
        name="Device1",
        serial="Serial1",
        manufacturer="Manufacturer1",
        product="Product1"
    )
    device_control.set_sample_rate(device, 2500000)  # 2.5 MHz
    mock_rtl.rtlsdr_set_sample_rate.assert_called_with(MagicMock(), 2500000)

def test_get_sample_rate(device_control, mock_rtl):
    device = SDRDevice(
        index=0,
        name="Device1",
        serial="Serial1",
        manufacturer="Manufacturer1",
        product="Product1"
    )
    rate = device_control.get_sample_rate(device)
    assert rate == 2000000
    mock_rtl.rtlsdr_get_sample_rate.assert_called_with(MagicMock())

def test_set_gain(device_control, mock_rtl):
    device = SDRDevice(
        index=0,
        name="Device1",
        serial="Serial1",
        manufacturer="Manufacturer1",
        product="Product1"
    )
    device_control.set_gain(device, 15)
    mock_rtl.rtlsdr_set_tuner_gain.assert_called_with(MagicMock(), 15)

def test_get_gain(device_control, mock_rtl):
    device = SDRDevice(
        index=0,
        name="Device1",
        serial="Serial1",
        manufacturer="Manufacturer1",
        product="Product1"
    )
    gain = device_control.get_gain(device)
    assert gain == 10
    mock_rtl.rtlsdr_get_tuner_gain.assert_called_with(MagicMock())

def test_start_and_stop_stream(device_control, mock_rtl):
    device = SDRDevice(
        index=0,
        name="Device1",
        serial="Serial1",
        manufacturer="Manufacturer1",
        product="Product1"
    )

    # Mock read_async and cancel_async
    with patch('src.ddrtlsdr.device_control.read_async') as mock_read_async, \
         patch('src.ddrtlsdr.device_control.cancel_async') as mock_cancel_async:
        
        callback = MagicMock()
        device_control.start_stream(device, callback, buffer_size=16384)
        mock_read_async.assert_called_once()
        assert device.serial in device_control.streams

        device_control.stop_stream(device)
        mock_cancel_async.assert_called_once()
        assert device.serial not in device_control.streams
