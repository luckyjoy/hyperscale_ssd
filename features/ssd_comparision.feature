@all @compare
Feature: SSD Vendor Performance Comparison
  In order to validate SSD vendors
  As a performance engineer
  I want to compare sequential and random performance against requirements

  Background:
    Given a standardized test environment is configured

  Scenario Outline: <REQ_COM_01> Compare sequential read/write speeds
  #  Given the "<vendor>" SSD is connected
    Given the <vendor> SSD is connected
    When I run a sequential speed test for <time> seconds
    Then the reported sequential read speed should be at least <min_read_speed> MB/s
    And the reported sequential write speed should be at least <min_write_speed> MB/s

    Examples:
      |  vendor          | min_read_speed | min_write_speed | time |
      |  "Samsung 990"   | 6000           | 5000            | 120  |
      |  "SanDisk Pro"   | 500            | 450             | 120  |
      | "Pure Storage"   | 3000           | 2500            | 120  |

  Scenario Outline: <REQ_COM_02> Compare random 4K I/O performance
    #Given the "<vendor>" SSD is connected
	Given the <vendor> SSD is connected
    When I run a random 4K I/O test for <time> seconds
    Then the reported random read IOPS should be at least <min_read_iops>
    And the reported random write IOPS should be at least <min_write_iops>

    Examples:
      |   vendor        | min_read_iops | min_write_iops | time |
      | "Samsung 990"   | 800000        | 700000         | 120  |
      | "SanDisk Pro"   | 100000        | 90000          | 120  |
      | "Pure Storage"  | 500000        | 450000         | 120  |
