@ECHO OFF
ECHO.
ECHO ========================================
ECHO           TASM RUN MODE
ECHO ========================================
ECHO.

IF NOT EXIST C:\MAIN.EXE GOTO ERROR

ECHO Running C:\MAIN.EXE...
ECHO.
C:\MAIN.EXE

ECHO.
ECHO PROGRAM FINISHED.
HALT
GOTO END

:ERROR
ECHO.
ECHO C:\MAIN.EXE was not found.
ECHO Run BUILD mode first.
HALT

:END
