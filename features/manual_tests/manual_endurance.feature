@manual 
Feature: Manual Endurance and Wear-Leveling Check
  Confirm SSD health indicators after endurance workload.

  Scenario: <REQ_SSD_520> Validate SSD health after 1 PB written 
    Given the SSD has sustained a 24/7 sequential write workload for 1 PB
    When the operator collects SMART health data
    Then wear-leveling count should decrease within expected tolerance
    And no uncorrectable errors should be present
    And remaining life should report above 95%
