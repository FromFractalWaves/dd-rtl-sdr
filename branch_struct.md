dd-rtl-sdr/
├── .ctree
├── .gitignore
├── LICENSE
├── README.md
├── dev_guide.md
├── pyvenv.cfg
├── requirements.txt
├── setup.py
├── MANIFEST.in
├── src/
│   └── ddrtlsdr/
│       ├── __init__.py
│       ├── api.py
│       ├── gui.py
│       ├── device_control.py
│       ├── device_manager.py
│       ├── librtlsdr_wrapper.py
│       ├── models.py
│       ├── logging_config.py
│       ├── config.json
│       └── logs/
│           └── ddrtlsdr.log
├── start_linux.sh
├── start_api.sh
├── start_gui.sh
├── test_config.json
└── tests/
    ├── __init__.py
    ├── test_device_manager.py
    ├── test_device_control.py
    └── test_models.py
