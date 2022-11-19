@echo off
cd %~dp0
cmd /k "..\..\Scripts\activate & python -m imsearchtools.http_service 36213"
