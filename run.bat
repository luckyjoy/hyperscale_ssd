@echo off
echo Demo Hyperscale SSD Tests by Bang Thien Nguyen, ontario1998@gmail.com ...
echo behave --tags=@all --exclude "features/manual_tests/.*" -f html-pretty -o reports\validation_report.htmlecho 

if not exist reports mkdir reports
del /q reports\*.html
behave --tags=@all --exclude "features/manual_tests" -f html-pretty -o reports\validation_report.html
python scenarios_auto_pertcentage.py
python test_coverage.py reports/ssd_requirements.csv

rem Get the current date and time and format them for the filename.
rem Use a fixed date format without the day of the week.
set "current_date=%date%"
set "current_date=%current_date:~-10%"
set "current_date=%current_date:/=-%"
set "current_time=%time::=-%"

rem Remove spaces from the date and time.
set "current_date=%current_date: =%"
set "current_time=%current_time: =%"
rem Construct the new filename with the timestamp.
set destination_file=reports\report_%current_date%_%current_time%.html
rem Set the original file name.
set "source_file=reports\validation_report.html"

rem Get the current date and time and format them for the filename.
rem Use a fixed date format without the day of the week.
set "current_date=%date%"
set "current_date=%current_date:~-10%"
set "current_date=%current_date:/=-%"
set "current_time=%time::=-%"

rem Remove spaces from the date and time.
set "current_date=%current_date: =%"
set "current_time=%current_time: =%"

rem Construct the new filename with the timestamp.
set "destination_file=validation_reportt_%current_date%_%current_time%.html"

rem Rename the file.
ren "%source_file%" "%destination_file%"

echo  * Validation Report Generated At: %destination_file% .

pause