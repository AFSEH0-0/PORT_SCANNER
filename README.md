# TCP Port Scanner

A simple multithreaded TCP port scanner written in Python 3 for Linux.

The scanner uses Python's built-in `socket` module to test TCP ports and
`ThreadPoolExecutor` to scan multiple ports concurrently.

Only OPEN ports are printed to the terminal and written to the log file.

---

## Features

- TCP connect scanning
- Scan a single host/IP address
- Scan a single port
- Scan a range of ports
- Multithreaded scanning
- Configurable timeout
- Hostname resolution
- Exception handling
- Ctrl+C handling
- Log file support
- Only displays OPEN ports
- No external Python packages required

---

## Requirements

- Linux
- Python 3.x

Check Python:

```bash
python3 --version
