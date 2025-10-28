@echo off

REM Navigate to your repository root
cd C:\my_work\hyperscale_ssd

echo %RANDOM% > dummy.txt
echo Add a dummy file dummy.txt
git add dummy.txt

REM Commit with message
echo.
echo Git pushed a dummy file for CI Demo
echo git commit -m "Pushed a dummy file to Trigger CI..."
git commit -m "Pushed a dummy file to Trigger CI..."

REM Ensure branch is main
echo git branch -M main
git branch -M main

REM Push to origin main
echo git push -u origin main
git push -u origin main

rem curl -u "luckyjoy:11ce1755fa745c0bf522d169a9cac2ca11" -k -X POST "https://localhost:8443/job/hyperscale_ssd/build"

echo Open Secured Jenkins Pipelines and GitHub Actions ...
sleep 10

rem start "" "https://localhost:8443/view/all/builds"

start "" "https://github.com/luckyjoy/hyperscale_ssd/actions"

echo.

echo A new build has been triggred at secured Jenkins server: https://localhost:8443/view/all/builds
echo.

echo A new build has been trigger at GitHub server: "https://github.com/luckyjoy/hyperscale_ssd/actions"
del dummy.txt
echo.