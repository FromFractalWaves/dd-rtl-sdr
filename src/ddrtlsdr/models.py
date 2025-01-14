# src/ddrtlsdr/models.py

from pydantic import BaseModel, Field, field_validator
from typing import List

class SDRDevice(BaseModel):
    index: int = Field(..., ge=0, description="Device index")
    name: str = Field(..., description="Device name")
    serial: str = Field(..., description="Device serial number")
    manufacturer: str = Field(..., description="Device manufacturer")
    product: str = Field(..., description="Device product name")

    @field_validator('serial')
    def serial_not_empty(cls, v):
        if not v:
            raise ValueError("serial cannot be empty")
        return v

    @field_validator('manufacturer')
    def manufacturer_not_empty(cls, v):
        if not v:
            raise ValueError("manufacturer cannot be empty")
        return v

    @field_validator('product')
    def product_not_empty(cls, v):
        if not v:
            raise ValueError("product cannot be empty")
        return v

class SDRConfig(BaseModel):
    devices: List[SDRDevice] = Field(default_factory=list, description="List of SDR devices")

    def save(self, file_path: str):
        with open(file_path, "w") as f:
            f.write(self.model_dump_json(indent=4))  # Updated method

    @staticmethod
    def load(file_path: str):
        with open(file_path, "r") as f:
            return SDRConfig.model_validate_json(f.read())  # Updated method
