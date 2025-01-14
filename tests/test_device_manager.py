# tests/test_device_manager.py

import pytest
from unittest.mock import patch, MagicMock

from src.ddrtlsdr.device_manager import DeviceManager
from src.ddrtlsdr.models import SDRDevice, SDRConfig

@pytest.fixture
def mock_rtl():
    with patch('src.ddrtlsdr.librtlsdr_wrapper.rtl') as mock_rtl_lib:
        mock_rtl_lib.rtlsdr_get_device_count.return_value = 2
        mock_rtl_lib.rtlsdr_get_device_name.side_effect = [b'Device1', b'Device2']
        mock_rtl_lib.rtlsdr_get_device_usb_strings.side_effect = [
            0,  # Success for first device
            0   # Success for second device
        ]
        return mock_rtl_lib

@pytest.fixture
def device_manager(mock_rtl, tmp_path):
    config_file = tmp_path / "config.json"
    return DeviceManager(config_file=str(config_file))

def test_enumerate_devices(device_manager, mock_rtl):
    # Mock USB string buffers
    def mock_get_device_usb_strings(i, manufacturer, product, serial):
        if i == 0:
            manufacturer.value = b'Manufacturer1'
            product.value = b'Product1'
            serial.value = b'Serial1'
            return 0
        elif i == 1:
            manufacturer.value = b'Manufacturer2'
            product.value = b'Product2'
            serial.value = b'Serial2'
            return 0
        return -1

    mock_rtl.rtlsdr_get_device_usb_strings.side_effect = mock_get_device_usb_strings

    devices = device_manager.enumerate_devices()

    assert len(devices) == 2
    assert devices[0].name == "Device1"
    assert devices[0].manufacturer == "Manufacturer1"
    assert devices[0].product == "Product1"
    assert devices[0].serial == "Serial1"

    assert devices[1].name == "Device2"
    assert devices[1].manufacturer == "Manufacturer2"
    assert devices[1].product == "Product2"
    assert devices[1].serial == "Serial2"

def test_add_device_if_unrecognized(device_manager):
    device = SDRDevice(
        index=0,
        name="Device1",
        serial="Serial1",
        manufacturer="Manufacturer1",
        product="Product1"
    )
    device_manager.add_device_if_unrecognized(device)
    assert len(device_manager.config.devices) == 1
    assert device_manager.config.devices[0].serial == "Serial1"

    # Attempt to add the same device again
    device_manager.add_device_if_unrecognized(device)
    assert len(device_manager.config.devices) == 1  # Should not duplicate

def test_verify_device_accessibility_success(device_manager, mock_rtl):
    device = SDRDevice(
        index=0,
        name="Device1",
        serial="Serial1",
        manufacturer="Manufacturer1",
        product="Product1"
    )

    # Mock open_device and close_device to succeed
    with patch('src.ddrtlsdr.device_manager.open_device', return_value=MagicMock()) as mock_open, \
         patch('src/ddrtlsdr/device_manager.close_device', return_value=None) as mock_close:
        accessible = device_manager.verify_device_accessibility(device)
        assert accessible
        mock_open.assert_called_once_with(0)
        mock_close.assert_called_once_with(MagicMock())
