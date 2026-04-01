# Asset Kiosk System

A Raspberry Pi–based smart asset and tool management kiosk for **check-in / check-out**, **item search**, **consumable tracking**, and **admin management** using:

- QR code scanning
- Barcode scanning
- RFID card/tag reading
- Face verification
- SQLite database logging
- Tkinter-based kiosk UI

This project is designed for workshop, lab, warehouse, and engineering environments where tools, assets, and consumables need to be tracked efficiently.

---

## Features

### User-side features
- Tool / asset **take** and **return** workflow
- Scan items using:
  - QR
  - Barcode
  - RFID
- **Face verification** before transaction completion
- Search items by category
- Consumable quantity selection
- Touchscreen-style kiosk interface

### Admin-side features
- Admin login with PIN
- Add users with:
  - Person ID
  - Name
  - Email
  - RFID card/tag
  - Face samples
- Add and manage:
  - Tools
  - Assets
  - Components
  - Consumables
- View item status
- Manage users
- View transaction history
- Export transaction history to CSV / USB

---

## Project Overview

The Asset Kiosk System is a self-service smart kiosk that allows users to issue and return tools or assets using multiple authentication and identification methods. The system supports QR/barcode scanning, RFID-based identification, and face verification, while maintaining transaction logs in a local SQLite database.

It is suitable for:
- Tool room automation
- Warehouse asset issue/return
- Lab equipment tracking
- Consumable stock issue
- Engineering and industrial environments

---

## Project Modules

### Main application
- `app.py`  
  Main entry point of the kiosk application. Handles navigation between different UI screens.

### Configuration
- `config.py`  
  Stores screen settings, database paths, face model paths, camera indexes, tag modes, and admin PIN.

### Database
- `db.py`  
  Handles SQLite database creation, item/user storage, transactions, search, and history export.

### User interface
- `ui_front.py`  
  Front landing page and welcome flow.

- `ui_flow.py`  
  Main check-in/check-out logic, scan flow, and verification flow.

- `ui_search.py`  
  Search interface for category/item lookup.

- `ui_consumable.py`  
  Quantity selection and consumable transaction handling.

- `ui_common.py`  
  Common helpers used across multiple UI pages.

- `ui_widgets.py`  
  Reusable custom widgets and UI button helpers.

- `ui_colors.py`  
  Centralized color constants for UI styling.

- `scroll_frame.py`  
  Scrollable frame support for long content pages.

- `rounded_button.py`  
  Rounded custom button widget support.

### Admin panel
- `admin_ui.py`  
  Admin dashboard for user management, item management, and transaction history.

### Camera / Scanner / Authentication
- `camera_widget.py`  
  Camera preview and capture support.

- `scanner.py`  
  QR/barcode decoding from camera frames.

- `rfid_rc522.py`  
  RC522 RFID reader integration.

- `rfid_reader.py`  
  RFID helper logic.

- `face_auth.py`  
  Face registration and verification logic.

### Audio feedback
- `sound.py`  
  Sound support helpers.

- `sound_gpio.py`  
  GPIO-triggered or event-triggered sound handling.

---

## Hardware Used

- Raspberry Pi 5
- Camera module / USB camera
- RC522 RFID reader
- Touchscreen / display
- RFID tags/cards
- Speaker / buzzer for feedback

---

## Software Stack

- Python 3
- Tkinter
- OpenCV
- Pyzbar
- Pillow
- NumPy
- SQLite
- face_recognition
- MFRC522 / RFID library

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/asset-kiosk-system.git
cd asset-kiosk-system

#Install system dependencies
sudo apt update
sudo apt install -y python3-pip libzbar0 python3-spidev python3-rpi.gpio

#Install python dependencies
pip3 install -r requirements.txt --break-system-packages

#Run
python3 app.py
