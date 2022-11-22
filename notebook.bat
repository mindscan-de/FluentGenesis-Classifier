pushd
cd %~dp0
set PYTHONPATH=%~dp0/src;%PYTHONPATH%
jupyter notebook
popd