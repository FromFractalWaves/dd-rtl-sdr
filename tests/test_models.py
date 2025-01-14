import pytest
from src.ddrtlsdr.models import SDRDevice, SDRConfig

def test_sdr_device_valid():
    device = SDRDevice(
        index=0,
        name="Device1",
        serial="Serial1",
        manufacturer="Manufacturer1",
        product="Product1"
    )
    assert device.index == 0
    assert device.name == "Device1"
    assert device.serial == "Serial1"
    assert device.manufacturer == "Manufacturer1"
    assert device.product == "Product1"

def test_sdr_device_invalid_empty_fields():
    # Test empty name
    with pytest.raises(ValueError) as excinfo:
        SDRDevice(
            index=0,
            name="",
            serial="Serial1",
            manufacturer="Manufacturer1",
            product="Product1"
        )
    assert "name cannot be empty" in str(excinfo.value)

    # Test empty serial
    with pytest.raises(ValueError) as excinfo:
        SDRDevice(
            index=0,
            name="Device1",
            serial="",
            manufacturer="Manufacturer1",
            product="Product1"
        )
    assert "serial cannot be empty" in str(excinfo.value)

    # Test empty manufacturer
    with pytest.raises(ValueError) as excinfo:
        SDRDevice(
            index=0,
            name="Device1",
            serial="Serial1",
            manufacturer="",
            product="Product1"
        )
    assert "manufacturer cannot be empty" in str(excinfo.value)

    # Test empty product
    with pytest.raises(ValueError) as excinfo:
        SDRDevice(
            index=0,
            name="Device1",
            serial="Serial1",
            manufacturer="Manufacturer1",
            product=""
        )
    assert "product cannot be empty" in str(excinfo.value)

def test_sdr_config_save_load(tmp_path):
    config = SDRConfig(devices=[
        SDRDevice(
            index=0,
            name="Device1",
            serial="Serial1",
            manufacturer="Manufacturer1",
            product="Product1"
        ),
        SDRDevice(
            index=1,
            name="Device2",
            serial="Serial2",
            manufacturer="Manufacturer2",
            product="Product2"
        )
    ])
    config_file = tmp_path / "config.json"
    config.save(str(config_file))

    loaded_config = SDRConfig.load(str(config_file))
    assert len(loaded_config.devices) == 2
    assert loaded_config.devices[0].serial == "Serial1"
    assert loaded_config.devices[1].serial == "Serial2"
