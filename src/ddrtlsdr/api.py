# src/ddrtlsdr/api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from .device_control import DeviceControl
from .models import SDRDevice

app = FastAPI(title="DDRTLSDR API")

device_control = DeviceControl()

class FrequencyUpdate(BaseModel):
    frequency_hz: int

class SampleRateUpdate(BaseModel):
    sample_rate_hz: int

class GainUpdate(BaseModel):
    gain: int

@app.get("/devices", response_model=List[SDRDevice])
def list_devices():
    return device_control.manager.config.devices

@app.post("/devices/{serial}/frequency")
def set_frequency(serial: str, freq: FrequencyUpdate):
    device = next((d for d in device_control.manager.config.devices if d.serial == serial), None)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device_control.set_center_frequency(device, freq.frequency_hz)
    return {"message": f"Frequency set to {freq.frequency_hz} Hz for device {serial}"}

@app.post("/devices/{serial}/sample_rate")
def set_sample_rate(serial: str, sample_rate: SampleRateUpdate):
    device = next((d for d in device_control.manager.config.devices if d.serial == serial), None)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device_control.set_sample_rate(device, sample_rate.sample_rate_hz)
    return {"message": f"Sample rate set to {sample_rate.sample_rate_hz} Hz for device {serial}"}

@app.post("/devices/{serial}/gain")
def set_gain(serial: str, gain: GainUpdate):
    device = next((d for d in device_control.manager.config.devices if d.serial == serial), None)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device_control.set_gain(device, gain.gain)
    return {"message": f"Gain set to {gain.gain} for device {serial}"}

# Add more endpoints as needed
