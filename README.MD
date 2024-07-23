GreytHR Login
Requirements:
To schedule you need VPS Server in my case i was using AWS Instance:
To set up Selenium on an Ubuntu AWS instance for headless Chrome, you'll need to install Chrome, the Chrome driver, and configure Selenium to use them.
Here’s a step-by-step guide to help you through the process:
Step 1: Install Chrome and Chrome Driver
sudo apt-get update
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip  // checkout for Latest Version
sudo apt-get install unzip
unzip chromedriver_linux64.zip
sudo chmod +x chromedriver
sudo mv chromedriver /usr/local/bin/
chromedriver --version

Step 2: Install Python and Selenium
Most AWS instances come with Python installed. Check the version:
python3 --version
If not installed, install Python
sudo apt-get install python3
sudo apt install python3-selenium
pip install webdriver-manager

Step 3: Set Environment Variables
export GREYTHR_USERNAME=your_username
export GREYTHR_PASSWORD=your_password

Step 4: Checking manually whether the script is running or not
python3 script.py

Step 5: Schedule the crontab (Cronjobs)
45 13 * * * export GREYTHR_USERNAME='your_username'; export GREYTHR_PASSWORD='your_password'; /usr/bin/python3 /path/to/your/login.py >> /path/to/your/login.log 2>&1
