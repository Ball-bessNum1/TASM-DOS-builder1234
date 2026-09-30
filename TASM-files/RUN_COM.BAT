@ECHO OFF
ECHO.
ECHO ========================================
ECHO           TASM RUN MODE
ECHO ========================================
ECHO.

IF NOT EXIST C:\MAIN.EXE GOTO ERROR

ECHO Running C:\MAINCOM.COM...
ECHO.
C:\MAINCOM.COM

ECHO.
ECHO PROGRAM FINISHED.
IF EXIST C:\HALT.EXE C:\HALT.EXE
GOTO END

:ERROR
ECHO.
ECHO C:\MAINCOM.COM was not found.
ECHO Run BUILD mode first.
IF EXIST C:\HALT.EXE C:\HALT.EXE

:END
