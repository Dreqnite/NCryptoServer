@echo off

@rem if user forgot to specify a flag
if "~%1" == "" (
	@echo Incorrect syntax!
	@echo Syntax: build-database.bat [-fill,-empty,-help]
	goto END
)

@set mode="%1"

@rem if flag is incorrect
if %mode% neq "-fill" if %mode% neq "-empty" if %mode% neq "-help" (
	@echo Incorrect flag! Write 'build-database.bat -help' to see supported flags.
	goto END
)

@rem Shows help information about supported modes
if %mode% equ "-help" (
	@echo Syntax: build-database.bat [-fill,-empty,-help]
	@echo -empty - just creates an empty database;
	@echo -fill  - creates a database and fills it with a testing data;
	@echo -help  - shows supported modes.
	goto END
)

@rem Checks if database folder exists
if not exist NCryptoServer\db (
	@echo Creating database folder...
	mkdir NCryptoServer\db
)

@rem Checks if folder already contains needed database
if exist NCryptoServer\db\NCryptoDatabase.db (
	@echo Error! File NCryptoDatabase.db already exists!
	goto END
)

@rem Builds empty database
@echo Creating NCrypto database...
sqlite3.exe NCryptoServer\db\NCryptoDatabase.db ".read create-db.sql"

@rem Fills database with a testing data
if %mode% equ "-fill" (
	@echo Filling NCrypto database with a testing data...
	sqlite3.exe NCryptoServer\db\NCryptoDatabase.db ".read fill-db.sql"
)

if %ERRORLEVEL% equ 0 (
	@echo Done.
) else (
	@echo An error has occured during execution! Error code: %ERRORLEVEL%
)

:END