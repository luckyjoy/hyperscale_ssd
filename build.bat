@echo off

rem === General Info and Cleanup ===
echo Hyperscale SSD Automation by Bang Thien Nguyen, ontario1998@gmail.com ...

if not exist reports mkdir reports 
del /q reports\*.html 2>nul
rem behave --tags=@all --exclude "features/manual_tests" --step_timeout=SECONDS -f html-pretty -o reports\automation_report.html
behave --tags=@all --exclude "features/manual_tests" -f html-pretty -o reports\automation_report.html
rem behave --tags=@all --exclude "features/manual_tests" -f allure_behave.formatter:AllureFormatter -o allure-results
rem Set the source file name.
set "source_file=reports\automation_report.html"

rem Get the current date and time.
set "current_date=%date%"
set "current_time=%time%"

rem Fix the date format (MM-DD-YYYY or system locale dependent).
set "current_date=%current_date:~4%"
set "current_date=%current_date:/=-%"
set "current_date=%current_date: =%"

rem Fix the time format for filename.
set "current_time=%current_time::=-%"
set "current_time=%current_time: =%"
set "current_time=%current_time:.=-%"

rem Build new filename (without path).
set "new_filename=automation_report_%current_date%_%current_time%.html"

rem Full destination path.
set "destination_file=reports\%new_filename%"

rem Rename if source exists.
if exist "%source_file%" (
    pushd reports
    ren "automation_report.html" "%new_filename%"
    popd
    echo * Automation Report Generated At: "%destination_file%".
) else (
    echo "%source_file%" was not found.
)

rem === Build Supporting Reports ===
rem The following scripts were updated to take a single <features_dir> argument.
echo.
echo Building Test Coverage Report...
python supports\test_coverage.py reports\ssd_requirements.csv features

echo.
echo Building PRD Summary Report...
python supports\prd2html.py supports\product.json supports\requirements.csv

echo.
echo Building Validation Plan...
python supports\validation_plan_builder.py reports\validation.json features

echo.
echo Building Automation Rate Metric...
python supports\automation_rate.py features

rem === Open Reports in Browser ===
echo.
echo Opening reports in browser...
sleep 3
for %%f in (reports\*.html) do (
    start "" "%%~f"
)

echo.
echo All Tasks Completed.
echo.
pause