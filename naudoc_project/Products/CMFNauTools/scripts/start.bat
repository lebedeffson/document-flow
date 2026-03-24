@echo off
set INSTANCE_HOME=%CD%
set ZOPE_HOME=%CD%\..\..
set SOFTWARE_HOME=%ZOPE_HOME%\lib\python

set PYTHON=%ZOPE_HOME%\bin\python.exe
set ZOPE_RUN=%ZOPE_HOME%\z2.py

setlocal
set PYTHON_OPTS=-O

set ZOPE_OPTS=-D

set HTTP_PORT=
set FTP_PORT=-
set WEBDAV_PORT=-
set PCGI_CONFIG=-

set STUPID_LOG_FILE=%INSTANCE_HOME%\var\Z2-debug.log
set STUPID_LOG_SEVERITY=-500

if Not %HTTP_PORT% == "" set ZOPE_OPTS=%ZOPE_OPTS% -w %HTTP_PORT%
if Not %FTP_PORT% == "" set ZOPE_OPTS=%ZOPE_OPTS% -f %FTP_PORT%
if Not %WEBDAV_PORT% == "" set ZOPE_OPTS=%ZOPE_OPTS% -W %WEBDAV_PORT%
if Not %PCGI_CONFIG% == "" set ZOPE_OPTS=%ZOPE_OPTS% -p %PCGI_CONFIG%

echo Starting Zope\NauDoc

"%PYTHON%" %PYTHON_OPTS% "%ZOPE_RUN%" %ZOPE_OPTS% %1 %2 %3 %4 %5 %6 %7 %8 %9
