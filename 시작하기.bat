@echo off
chcp 65001 >nul
echo YouTube to PPT 서비스를 시작합니다...
cd /d c:\Projects\youtube-to-ppt
py -3.14 -m streamlit run app.py
pause
