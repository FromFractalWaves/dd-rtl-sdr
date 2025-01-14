# src/ddrtlsdr/gui.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QLineEdit, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt

from .device_control import DeviceControl
from .models import SDRDevice

class SDRControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.device_control = DeviceControl()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("DDRTLSDR Control Panel")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Device Selection
        self.device_label = QLabel("Select Device:")
        self.device_combo = QComboBox()
        self.load_devices()
        layout.addWidget(self.device_label)
        layout.addWidget(self.device_combo)

        # Frequency Input
        self.freq_label = QLabel("Center Frequency (Hz):")
        self.freq_input = QLineEdit()
        layout.addWidget(self.freq_label)
        layout.addWidget(self.freq_input)

        # Sample Rate Input
        self.rate_label = QLabel("Sample Rate (Hz):")
        self.rate_input = QLineEdit()
        layout.addWidget(self.rate_label)
        layout.addWidget(self.rate_input)

        # Gain Input
        self.gain_label = QLabel("Gain:")
        self.gain_input = QLineEdit()
        layout.addWidget(self.gain_label)
        layout.addWidget(self.gain_input)

        # Set Parameters Button
        self.set_button = QPushButton("Set Parameters")
        self.set_button.clicked.connect(self.set_parameters)
        layout.addWidget(self.set_button)

        self.setLayout(layout)

    def load_devices(self):
        devices = self.device_control.manager.config.devices
        for device in devices:
            self.device_combo.addItem(f"{device.name} ({device.serial})", device)

    def set_parameters(self):
        device = self.device_combo.currentData()
        if not device:
            QMessageBox.warning(self, "Error", "No device selected.")
            return

        try:
            freq = int(self.freq_input.text())
            rate = int(self.rate_input.text())
            gain = int(self.gain_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid input. Please enter integer values.")
            return

        try:
            self.device_control.set_center_frequency(device, freq)
            self.device_control.set_sample_rate(device, rate)
            self.device_control.set_gain(device, gain)
            QMessageBox.information(self, "Success", "Parameters set successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

def main():
    app = QApplication(sys.argv)
    gui = SDRControlGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
