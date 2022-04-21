# NeosFen(nec)

This application is an experimentation for me to understand the NeosVR API. It have the ability to show your contacts status, online, offline, etc. It also show in which session the contact is present. The functionnality are pretty simple for now.

Feel free to use or hack.

Add python neos module by [mralext20](https://github.com/mralext20/neos.py),
this code will probably moved in another git repository so the license in the
neos folder only apply to the neos folder and subdirectories.

# Installation

This application should work on Linux and Windows.

Only a windows build is available here: https://github.com/brodokk/NeosFen/releases

Otherwise for Linux or other usage you can use this commands:

```
pip install -r requirements.txt
python app.py
```

## Build an executable for windows

If you still want to build yourself a version of the application use the following commands:

```
pip install -r requirements.txt
python -m PyInstaller .\neosfen.spec
```

Now you will be able to found the compiled version in `dist` folder.