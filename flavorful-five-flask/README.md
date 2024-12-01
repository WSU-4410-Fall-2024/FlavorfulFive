## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required dependencies

Create a .env file and add the following values (for sensitive data) 
Note:Your mail password might have to specifically be an app password.

   ```env
   MAIL_USERNAME=your_email@example.com
   MAIL_PASSWORD=your_email_password
   SECRET_KEY=your_secret_key
   OTP_SECRET_KEY=your_otp_secret_key
   ```

##### Windows:
```zsh
pip install -r requirements.txt 
```

##### macOS/Linux:
```zsh
pip3 install -r requirements.txt
```

## Usage

##### Windows:
```zsh
python app.py
```
##### macOS/Linux:
```zsh
python3 app.py
```
