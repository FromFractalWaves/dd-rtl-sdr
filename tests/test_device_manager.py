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
    # Mock the number of devices
    mock_rtl.rtlsdr_get_device_count.return_value = 2

    # Mock device names
    mock_rtl.rtlsdr_get_device_name.side_effect = [b"Device1", b"Device2"]

    # Mock USB string buffers
    def mock_get_device_usb_strings(i, manufacturer, product, serial):
        if i == 0:
            manufacturer.value = b"Manufacturer1"
            product.value = b"Product1"
            serial.value = b"Serial1"
            return 0
        elif i == 1:
            manufacturer.value = b"Manufacturer2"
            product.value = b"Product2"
            serial.value = b"Serial2"
            return 0
        return -1

    mock_rtl.rtlsdr_get_device_usb_strings.side_effect = mock_get_device_usb_strings

    # Run the method under test
    devices = device_manager.enumerate_devices()

    # Validate results
    assert len(devices) == 2
    assert devices[0].name == "Device1"
    assert devices[0].manufacturer == "Manufacturer1"
    assert devices[0].product == "Product1"
    assert devices[0].serial == "Serial1"

    assert devices[1].name == "Device2"
    assert devices[1].manufacturer == "Manufacturer2"
    assert devices[1].product == "Product2"
    assert devices[1].serial == "Serial2"


def test_verify_device_accessibility_success(device_manager, mock_rtl):
    device = SDRDevice(
        index=0,
        name="Device1",
        serial="Serial1",
        manufacturer="Manufacturer1",
        product="Product1"
    )

    # Create a consistent MagicMock for the device handle
    mock_handle = MagicMock()

    # Mock open_device and close_device with consistent handle
    with patch("src.ddrtlsdr.device_manager.open_device", return_value=mock_handle) as mock_open, \
         patch("src.ddrtlsdr.device_manager.close_device") as mock_close:
        accessible = device_manager.verify_device_accessibility(device)

        # Validate results
        assert accessible
        mock_open.assert_called_once_with(0)
        mock_close.assert_called_once_with(mock_handle)


def test_verify_device_accessibility_failure(device_manager, mock_rtl):
    device = SDRDevice(
        index=0,
        name="Device1",
        serial="Serial1",
        manufacturer="Manufacturer1",
        product="Product1"
    )

    # Mock open_device to raise IOError
    with patch('src.ddrtlsdr.device_manager.open_device', side_effect=IOError("Device locked")):
        accessible = device_manager.verify_device_accessibility(device)
        assert not accessible
