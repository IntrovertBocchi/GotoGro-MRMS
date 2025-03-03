# GotoGro-MRMS

# Contributions

This project was entirely developed by Kai (@IntrovertBocchi).
I was responsible for:

- Project architecture and development
- Writing Python and Django code
- Setting up the database and local server
- Writing the entire setup and installation guide (this README)
- Any additional features and improvements

# Functionalities 

For this project, there were many functionalities I have included such as:

1. Separate view between admin and ordinary users
2. quantity logic
3. alerts
4. forecasting
5. password and login visibility

# Separate views 

Separating views was important in a management system where admins and ordinary users co-exist, to emulate workplace environments where privacy is maintained, I have implemented separated views for different users in the system.

https://github.com/user-attachments/assets/425b5489-ae13-4557-b350-1df83057ae04

# Quantity logic

One of the challenges was quantity logic, since the application dealt with available inventory and purchase amount, in which the purchased amount should not exceed available inventory (as it means that you're selling more than you have), this is a video demonstration of how I have implemented this quantity logic.

# Quantity logic 1.0 - Purchase amount should not exceed available inventory

This is one of the logics where the purchase amount must not exceed available inventory

https://github.com/user-attachments/assets/5b828bc5-6753-42fb-8d25-8f4bb534d3c2


# Quantity logic 2.0 - Inventory cannot be less than purchase amount 

Below deals with the quantity logic that the inventory cannot be lower than the purchase amount for update quantity and inventory.

https://github.com/user-attachments/assets/86de0994-c280-4ce3-ab69-d6e37ee3bbff

https://github.com/user-attachments/assets/3d7dcb36-1e9a-4c99-af69-7355cddb0ca2


# Alerts

Any amount from 100-1000, it will send an alert to the superuser, it will also notify if the inventory levels are low.

https://github.com/user-attachments/assets/3afe315f-22dd-422d-a16a-83d02695784e


# Forecasting

I have also implemented a simple forecasting system so that whenever the purchase quantity is changed, it reflects back to the purchase quantity multiplied by two depending on the demand.

https://github.com/user-attachments/assets/f475701f-3014-4b2d-93a7-5868a14e6bba



# Password and Login

for the login page, I implemented a clear field every time a user logs in to the page. I also implemented a workaround for saved passwords on some browsers. emphasizing on data security and taking into consideration shared environments where sensitive information is shared.

https://github.com/user-attachments/assets/a2bac7ad-5e8c-4035-9080-c568906234a0



# Instruction Manual

Foreword: GotoGro-MRMS is built on a python base with django dependencies, hosted on a local server. Please follow the instructions below for this program to be able to work on your systems.

Install Python

Download Python: • Visit the official Python website and download the latest stable version (preferably Python 3.9 or later). https://www.python.org/downloads/

Install Python: • Run the installer and follow the prompts. • Important: During installation, check the box that says “Add Python to PATH”.

Verify Installation: • Open your terminal (Command Prompt on Windows, Terminal on macOS/Linux). • Run in cmd / terminal: python --version

Install Visual Studio Code

Download VS Code: • Visit the VS Code website and download the appropriate installer for your operating system.

Install VS Code: • Run the installer and follow the prompts.

Install Git

Download Git: • Visit the Git website and download the installer for your OS. https://git-scm.com/downloads

Install Git: • Run the installer and follow the prompts.

Verify Installation: • Open your terminal and run: git --version

Install Django

Open VS Code Terminal: • Open VS Code. • Open the integrated terminal by pressing Ctrl+` or navigating to View > Terminal.

Create a Project Directory: • Terminal (RUN ONCE): -- mkdir member_management • Terminal (RUN ONCE): -- cd member_management

Set Up a Virtual Environment: • It’s good practice to use a virtual environment to manage dependencies. • Terminal (RUN ONCE): python -m venv env

Activate the Virtual Environment: 4. Windows (ALWAYS START FIRST): • Terminal: env\Scripts\activate

macOS/Linux (ALWAYS START FIRST): • Terminal: source env/bin/activate

Upgrade pip (RUN ONCE) • pip install --upgrade pip

Install Django • Terminal and run (RUN ONCE): pip install django • Verify Django Installation using terminal: django-admin –version

Create a New Django Project 7. Start a New Project: • Terminal (RUN ONCE): django-admin startproject GotoGroMRMS

Navigate to the Project Directory: • Terminal (ALWAYS): cd GotoGroMRMS

Run the Development Server: • Terminal (RUN ALWAYS): python manage.py runserver • Open your browser and go to http://127.0.0.1:8000/ to see the Django welcome page.

Stop the Server: Press Ctrl+C in the terminal.

Basic Setup after Initialization

Windows (ALWAYS START FIRST): Terminal: env\Scripts\activate

macOS/Linux (ALWAYS START FIRST): Terminal: source env/bin/activate

Navigate to the Project Directory: Terminal (ALWAYS): cd GotoGroMRMS

Run the Development Server: Terminal (RUN ALWAYS): python manage.py runserver Note: if cannot try the option below- python manage.py runserver 127.0.0.1:8080
