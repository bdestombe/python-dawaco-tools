# python-dawaco-tools
Tools to read the Dawaco database written in Python. Have a look at the tutorials folder to get started.

# Installation instructions
## Install ODBC driver
We need a ODBC driver to create the connection with the SQL database.

Download version 18 for x64 platform of the ODBC driver from the microsoft website. https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

## Install environment PWN employees
 - Create a project folder within a OneDrive location. This folder holds your personal scripts, data, and project related files. No dawacot
 - Use GitHub Desktop to clone github.com/bdestombe/python-dawaco-tools to this exact local directory: "C:\PythonScripts\Repositories\bdestombe\python-dawaco-tools"
 - VSCode > Open Folder: project folder > Command prompt
   - Create `C:\PythonScripts\Environments\dawacotools` folder
   - `uv venv --python=3.13 --directory=C:\PythonScripts\Environments\dawacotools`
   - `C:\PythonScripts\Environments\dawacotools\.venv\Scripts\activate`
   - `uv pip install -e "C:\PythonScripts\Repositories\bdestombe\python-dawaco-tools"`
   - <kbd> <br> Ctrl <br> </kbd> + <kbd> <br> Shift <br> </kbd> + <kbd> <br> P <br> </kbd> => "Python: Select Interpreter" => "Enter interpreter path..." => `C:\PythonScripts\Environments\dawacotools\.venv\Scripts\python.exe`

The environment is now installed in `C:\PythonScripts\Environments\dawacotools\.venv\Scripts\python.exe`
