# NeosFen(nec)

This application is an experimentation for me to understand the NeosVR API. It have the ability to show your contacts status, online, offline, etc. It also show in which session the contact is present. The functionnality are pretty simple for now and the developement is a bit halted for now until a proper way to build the client for Windows is implemented. Feel free to use or hack.

Add python neos module by [mralext20](https://github.com/mralext20/neos.py),
this code will probably moved in another git repository so the license in the
neos folder only apply to the neos folder and subdirectories.

# Usage

You can directly use it with the following commands:
```
pip install -r requirements.txt
python app.py
```

This application should work on Linux and Windows.

# Build on Windows

You can compile an executable for windows following the kivy documentation: https://kivy.org/doc/stable/guide/packaging-windows.html

But you could just run the following command for generate the `.spec` file:
```
python -m PyInstaller --name neosfen .\src\app.py
```

Before the next command you will need to add, manually for the moment two things. The first one is the dependencies at the start of the `.spec` file:
```
from kivy_deps import sdl2, glew
```

Then you will need to add a `COLLECT`  for add some other file who are needed to the `.spec` file. Dont forgot to change the path of the `Tree` function to fit your system. I wanted to use the automatic detection of library dependency like indicated in the kivy documentation but it didnt work, so here your have my version who work on my computer.
```
coll = COLLECT(exe, Tree('src'),
               a.binaries,
               a.zipfiles,
               a.datas,
               Tree('C:\\Users\\fuck_off_microsoft\\AppData\\Local\\Programs\\Python\\Python39\\share\\sdl2\\bin\\'),
               Tree('C:\\Users\\fuck_off_microsoft\\AppData\\Local\\Programs\\Python\\Python39\\share\\glew\\bin\\'),
               strip=False,
               upx=True,
               name='neosfen')
```

Then you build the application with:
```
python -m PyInstaller .\neosfen.spec
```

Now you will be able to found the compiled version in `dist` folder.
