@echo off
setlocal ENABLEDELAYEDEXPANSION
title Hyperscale SSD Simulation Test Runner
chcp 65001 >nul

rem =====================[ ANSI Color Definitions ]=====================
rem Define ANSI escape codes for flicker-free color changes.
rem ESC [ 3X m is foreground color; ESC [ 0m is reset.
rem The ESC character (0x1B) is created using 'echo' and 'set /p' trick.
for /f %%a in ('echo prompt $E^| cmd') do set "ESC=%%a"

rem Colors (Foreground):
set "FG_HEADER=%ESC%[92m"  rem Bright Green
set "FG_STEP=%ESC%[93m"    rem Bright Yellow
set "FG_OK=%ESC%[32m"      rem Green
set "FG_WARN=%ESC%[33m"    rem Yellow
set "FG_ERROR=%ESC%[31m"   rem Red
set "FG_RESET=%ESC%[0m"    rem Reset

rem =====================[ REQUIRED ARGUMENT CHECK ]=====================
if "%~1" == "" goto missing_argument

set "BUILD_NUMBER=%~1"

rem Set TEST_SUITE using delayed expansion to handle potential special characters like @ more safely
if "%~2" == "" (
    set "TEST_SUITE=@all"
) else (
    set "TEST_SUITE=%~2"
)

rem =====================[ Header ]=====================
echo %FG_HEADER%
echo =============================================================
echo     🤖  Hyperscale SSD Simulation Test Runner (Build #%BUILD_NUMBER%)
echo     Author: Bang Thien Nguyen  ^|  ontario1998@gmail.com
echo =============================================================
echo %FG_RESET%
echo.

set "START_TIME=%time%"

rem =====================[ Step 1 ]=====================
echo %FG_STEP%[STEP 1/8] Cleaning up previous test artifacts...%FG_RESET%
rem Preserve 'allure-report' for history, only remove the volatile results and cache
rmdir /s /q allure-results __pycache__ .pytest_cache >nul 2>&1
mkdir allure-results >nul 2>&1
echo %FG_OK%[OK] Cleanup completed. History preserved in 'allure-report'.%FG_RESET%
echo.

rem =====================[ Step 2 ]=====================
echo %FG_STEP%[STEP 2/8] Building Test Coverage Report...%FG_RESET%
python supports\test_coverage.py supports\requirements.csv features
echo %FG_OK%[OK] Test Coverage Generated.%FG_RESET%
echo.

rem =====================[ Step 3 ]=====================
echo %FG_STEP%[STEP 3/8] Building Automation Rate Metric...%FG_RESET%
python supports\automation_rate.py features
echo %FG_OK%[OK] Automation Rate Generated.%FG_RESET%
echo.

rem =====================[ Step 4 ]=====================
echo %FG_STEP%[STEP 4/8] Generating PRD Summary Report...%FG_RESET%
python supports\prd2html.py supports\product.json supports\requirements.csv
echo %FG_OK%[OK] PRD Summary Generated.%FG_RESET%
echo.

rem =====================[ Step 5 ]=====================
echo %FG_STEP%[STEP 5/8] Building Validation Plan...%FG_RESET%
python supports\validation_plan_builder.py supports\validation.json features supports\requirements.csv
echo %FG_OK%[OK] Validation Plan Generated.%FG_RESET%
echo.

rem =====================[ Step 6 ]=====================
echo %FG_STEP%[STEP 6/8] Running Behave Test Suites (Tag: %TEST_SUITE%) (results → allure-results)...%FG_RESET%
rem Use quotes around %TEST_SUITE% just in case it contains spaces or other troublesome characters
echo behave --tags=%TEST_SUITE% --exclude "features/manual_tests" --format allure_behave.formatter:AllureFormatter -o allure-results
behave --tags="%TEST_SUITE%" --exclude "features/manual_tests" --format allure_behave.formatter:AllureFormatter -o allure-results
if %ERRORLEVEL% NEQ 0 (
  echo %FG_WARN%[WARN] Some tests FAILED during execution.%FG_RESET%
  set "TEST_STATUS=FAILED"
) else (
  echo %FG_OK%[OK] All tests PASSED.%FG_RESET%
  set "TEST_STATUS=PASSED"
)
echo.

rem =====================[ Step 7 ]=====================
echo %FG_STEP%[STEP 7/8] Generating Allure Report with Build History (Build #%BUILD_NUMBER%)...%FG_RESET%

rem A. Copy previous history from the old report into the new results folder
echo Copying previous history from 'allure-report\history' to 'allure-results\history'...
xcopy /E /I /Y "allure-report\history" "allure-results\history" >nul 2>&1
if exist "allure-report\history" (
    echo %FG_OK%[OK] Previous history copied.%FG_RESET%
) else (
    echo %FG_WARN%[WARN] History folder not found. Starting fresh trend.%FG_RESET%
)


rem B. Copy static environment and category files
copy supports\windows.properties allure-results\environment.properties >nul
copy supports\categories.json allure-results\ >nul

rem C. Generate dynamic executor.json file containing the build number for history trend
set "REPORT_URL=http://localhost:8080/job/Hyperscale_SSD_Sim_Test_Job/%BUILD_NUMBER%/allure"
(
echo {
echo   "name": "Test Runner",
echo   "type": "Standalone Script",
echo   "url": "%REPORT_URL%",
echo   "buildOrder": %BUILD_NUMBER%,
echo   "buildName": "Build #%BUILD_NUMBER%",
echo   "buildUrl": "%REPORT_URL%",
echo   "reportName": "Hyperscale SSD Sim Test Report",
echo   "reportUrl": "%REPORT_URL%"
echo }
) > allure-results\executor.json
echo Generated allure-results\executor.json with build number %BUILD_NUMBER%.

rem D. Generate the final report, overwriting the old one. This command enables history trend.
echo Running: allure generate --clean allure-results -o allure-report
allure generate --clean allure-results -o allure-report
if %ERRORLEVEL% NEQ 0 (
    echo %FG_ERROR%[ERROR] Allure report generation failed!%FG_RESET%
) else (
    echo %FG_OK%[OK] Allure Report Generated successfully.%FG_RESET%
)
echo.

rem =====================[ Step 8 ]=====================
echo %FG_STEP%[STEP 8/8] Opening all generated .html reports...%FG_RESET%

rem Open the PRD Summary Report HTML
start "" "allure-report\prd_summary_report.html"

rem Open the Validation Plan HTML
start "" "allure-report\validation_plan.html"

echo %FG_OK%[OK] Local reports opened.%FG_RESET%
echo.

rem =====================[ Step 9 ]=====================

echo %FG_STEP%[STEP 9/9] Opening all generated .html allure-report...%FG_RESET%

echo %FG_STEP%[STEP 7/8] Generating Allure Report...%FG_RESET%
copy supports\windows.properties allure-results\environment.properties >nul
copy supports\categories.json allure-results\ >nul
copy supports\executor.json allure-results\ >nul

start "" cmd /c "allure open allure-report"

echo.

for %%f in (allure-report\*.html) do (
    echo Opening: %%f
    start "" "%%~f"
)
echo %FG_OK%[OK] All local allure-report opened.%FG_RESET%
echo.

rem =====================[ Completion Summary ]=====================
:cleanup
echo %FG_RESET%
set "END_TIME=%time%"
echo =============================================================
if "%TEST_STATUS%"=="FAILED" (
    echo %FG_ERROR%    ⚠️  PIPELINE COMPLETED WITH SOME TEST FAILURES%FG_RESET%
) else (
    echo %FG_OK%    ✅  PIPELINE COMPLETED SUCCESSFULLY%FG_RESET%
)
echo   Build Number: %BUILD_NUMBER%
echo   Test Suite:   %TEST_SUITE%
echo   Started at: %START_TIME%
echo   Ended at:   %END_TIME%"
echo =============================================================

echo.
pause
endlocal
exit /b 0

rem =====================[ Error Handling Label ]=====================
:missing_argument
echo %FG_ERROR%[ERROR] Build number is required to generate Allure history.%FG_RESET%
echo Usage: build.bat ^<BUILD_NUMBER^> [suite_tag]
echo Example: build.bat 101 ^@adv
echo Available tags: ^@all (default), ^@adv, ^@compare, ^@inject, ^@mixed, ^@perf
pause
endlocal
exit /b 1
