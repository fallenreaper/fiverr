# Alphazen

You will want to take a look at a preexisting tool called: tdameritrade.  It is located at: https://tdameritrade.readthedocs.io/en/latest/api.html

The initial test, just dumps to the console the list of accounts associated.

First thing is first:  You need to install the aapproperiate driver for selenium. This is a weird windows ism as pip doesnt install it.  Read more about it at: https://selenium-python.readthedocs.io/installation.html#detailed-instructions-for-windows-users
You will need to make sure the reference is in your PATH for windows.  This can be done with a google search as to how to add files to your path.

Go use pip to install the requirements.
```pip3 install -r requirements.txt```

After that installs, you can edit config file as needed which will have access to relevant globals

Then you can run the application:  `python3 initialization.py` which will do a proof of concept and then create a token json file.


