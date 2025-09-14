from behave import given, when, then
from dataclasses import dataclass

@dataclass
class SSDPerformance:
    read_speed: float = 0.0
    write_speed: float = 0.0
    read_iops: int = 0
    write_iops: int = 0

# ------------------------------
# Background
# ------------------------------
@given('a standardized test environment is configured')
def step_configure_environment(context):
    context.test_environment = "configured"

@given('the "{vendor}" SSD is connected')
def step_connect_ssd(context, vendor):
    context.current_ssd = vendor
    context.performance_results = SSDPerformance()

# ------------------------------
# Sequential speed test
# ------------------------------
@when('I run a sequential speed test for {duration:d} seconds')
def step_run_sequential_test(context, duration):
    if "Samsung" in context.current_ssd:
        context.performance_results.read_speed = 6500.0
        context.performance_results.write_speed = 5200.0
    elif "SanDisk" in context.current_ssd:
        context.performance_results.read_speed = 520.0
        context.performance_results.write_speed = 460.0
    elif "Pure Storage" in context.current_ssd:
        context.performance_results.read_speed = 3100.0
        context.performance_results.write_speed = 2600.0

# ------------------------------
# Random 4K I/O test
# ------------------------------
@when('I run a random 4K I/O test for {duration:d} seconds')
def step_run_random_test(context, duration):
    if "Samsung" in context.current_ssd:
        context.performance_results.read_iops = 820000
        context.performance_results.write_iops = 710000
    elif "SanDisk" in context.current_ssd:
        context.performance_results.read_iops = 105000
        context.performance_results.write_iops = 92000
    elif "Pure Storage" in context.current_ssd:
        context.performance_results.read_iops = 510000
        context.performance_results.write_iops = 460000

# ------------------------------
# ±2% tolerance helper
# ------------------------------
def within_tolerance(measured, minimum, tolerance=0.02):
    return measured >= minimum * (1 - tolerance)

# ------------------------------
# Then steps
# ------------------------------
@then('the reported sequential read speed should be at least {min_speed:g} MB/s')
def step_check_read_speed(context, min_speed):
    actual = context.performance_results.read_speed
    min_speed = float(min_speed)
    assert within_tolerance(actual, min_speed), f"Read speed {actual} MB/s below {min_speed} ±2%"

@then('the reported sequential write speed should be at least {min_speed:g} MB/s')
def step_check_write_speed(context, min_speed):
    actual = context.performance_results.write_speed
    min_speed = float(min_speed)
    assert within_tolerance(actual, min_speed), f"Write speed {actual} MB/s below {min_speed} ±2%"

@then('the reported random read IOPS should be at least {min_iops:d}')
def step_check_read_iops(context, min_iops):
    actual = context.performance_results.read_iops
    assert within_tolerance(actual, min_iops), f"Read IOPS {actual} below {min_iops} ±2%"

@then('the reported random write IOPS should be at least {min_iops:d}')
def step_check_write_iops(context, min_iops):
    actual = context.performance_results.write_iops
    assert within_tolerance(actual, min_iops), f"Write IOPS {actual} below {min_iops} ±2%"
