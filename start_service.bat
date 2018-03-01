@echo off
cd %~dp0
cmd /k "..\..\Scripts\activate & python imsearch_http_service.py 36213"

