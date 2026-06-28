# pyTestFlow_demo
This repo contains the demonstration files for operating and testing an NI USB-6009 and RS RS-3005P with PyTestFlow.

When PyTestFlow has been installed, your folder contents should look something like the below.

```text
project_root/
├── .venv/
├── custom_step_types/
├── process_models/
├── test_reports/
├── test_sequences/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── basic_sequence.py
│   ├── message_box_and_flow_control.py
│   ├── motherboard_test_sequence.py
│   └── step_types_quickstart.py
└── config.yaml
```

The test_sequence folder is where we're going to place the files from this repo.

Below is what the test_sequence folder should look like after the files have been added.

```text
test_sequences/
├── __pycache__/
├── drivers/
│   ├── config.ini
│   ├── daq.py
│   └── psu.py
├── __init__.py
├── basic_sequence.py
├── message_box_and_flow_control.py
├── motherboard_test_sequence.py
├── step_types_quickstart.py
└── demo.py
```