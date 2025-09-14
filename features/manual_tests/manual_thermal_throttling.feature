@manual
Feature: Manual Thermal Throttling Validation
  Ensure SSD firmware properly throttles under high-temperature conditions.

  Scenario: <REQ_SSD_412> Validate throttling behavior at 85°C 
    Given the SSD is operating inside a thermal chamber at 85°C
    When the operator monitors SSD performance with fio workload
    Then throughput should gradually reduce to safe operating limits
    And no unexpected drive resets should occur
    And SMART attributes should log thermal throttling events
