# NCryptoServer
A server-side application of the NCryptoChat. This project is created with a purpose of studying Python, so it is not recommended to use NCryptoServer in real projects.

## How to install and use NCryptoServer
### To run NCryptoServer SQLite3 is needed:
* Download precompiled binaries of SQLite3 ([link](https://www.sqlite.org/download.html));  
* Create a folder `C:\Program Files (x86)\SQLite3` and unzip zipped files in this folder. Files should contain: `sqlite3.exe`, `sqlite3.dll`, `sqlite3.def`;
* Add `C:\Program Files (x86)\SQLite3` to the `PATH` environment variable.

### NCryptoServer can be installed in several ways:  
**Using PyPi:**
* Install distributions which are stored in PyPi: `pip install NCryptoServer`. NCryptoTools, which is required to run the NCryptoServer, will be installed automatically.
* If installation is successfull, it will be possible to run application in a two modes:
  * Console mode (all errors and warnings will be showed): `NCryptoServer_console`.
  * GUI mode (all errors and warnings will be hidden): `NCryptoServer_gui`.  

**Using this repository:**
* Install NCryptoTools from PyPi: `pip install NCryptoTools`.
* Clone this repository to your local computer.
* Run `build-database.bat` to build the SQLite3 database for the NCryptoServer with a testing data. Use `build-database.bat -help` to see build options.
* From the root directory of the NCryptoServer project execute in the console: `python -m NCryptoServer.launcher`.