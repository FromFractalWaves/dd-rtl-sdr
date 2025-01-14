# src/ddrtlsdr/models.py

from pydantic import BaseModel, Field, field_validator
from typing import List

class SDRDevice(BaseModel):
    index: int = Field(..., ge=0, description="Device index")
    name: str = Field(..., description="Device name")
    serial: str = Field(..., description="Device serial number")
    manufacturer: str = Field(..., description="Device manufacturer")
    product: str = Field(..., description="Device product name")

    @field_validator('serial', 'manufacturer', 'product')
    def not_empty(cls, v, field):
        if not v:
            raise ValueError(f"{field.name} cannot be empty")
        return v

class SDRConfig(BaseModel):
    devices: List[SDRDevice] = Field(default_factory=list, description="List of SDR devices")

    def save(self, file_path: str):
        with open(file_path, "w") as f:
            f.write(self.json(indent=4))

    @staticmethod
    def load(file_path: str):
        with open(file_path, "r") as f:
            return SDRConfig.parse_raw(f.read())
