from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List

class SDRDevice(BaseModel):
    model_config = ConfigDict(strict=True)  # Enables stricter validation
    index: int = Field(..., ge=0, description="Device index")
    name: str = Field(..., description="Device name")
    serial: str = Field(..., description="Device serial number")
    manufacturer: str = Field(..., description="Device manufacturer")
    product: str = Field(..., description="Device product name")

    @field_validator('name', 'serial', 'manufacturer', 'product')
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
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
