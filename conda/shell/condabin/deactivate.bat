:: Copyright (C) 2012 Anaconda, Inc
:: SPDX-License-Identifier: BSD-3-Clause

:: disable displaying the command before execution
@ECHO OFF

ECHO DeprecationWarning: 'deactivate' is deprecated. Use 'conda deactivate'. 1>&2
CALL "%~dp0\conda_hook.bat"
conda deactivate %*
