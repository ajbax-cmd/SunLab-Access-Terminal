# Sun Lab Access Terminal

A class assignment for CMPSC 487W that uses Python GUI application that interfaces with a MySQL database to manage user access in the Sun Lab.

## Features

- **User Authentication**: Secure login to the system using a password.
- **ID Management**: Activate, suspend, and reactivate user IDs.
- **Access Logs**: Browse and search through Sun Lab access logs by date, time, or user ID.
- **Change Password**: System administrators can change the password for accessing the terminal.

## Prerequisites

- MySQL 8.0.34 (or newer)
- Python 3.x
- PySimpleGUI

## Installation

### Setup Database:

1. Import the given SQL schema into your MySQL instance.
2. Adjust the `connection()` function to match your database credentials.

### Install Dependencies:

```bash
pip install PySimpleGUI mysql-connector-python
```

### Clone the Repository:

```bash
git clone <repository_url>
cd <repository_directory>
```

### Run the Application:
```bash
python main.py
```

### Usage

- **Login**: Use the password set in `password.txt` to log into the system.
- **Main Menu**: Navigate to various functionalities like activating a user ID, suspending access, etc.
- **Access Logs**: Filter through logs using user ID, specific date range, or specific time range.
- **Change Password**: Navigate to this option to change the system access password.

# License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.




