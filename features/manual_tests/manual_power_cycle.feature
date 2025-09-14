@manual
Feature: Manual Power Cycling Stress Test
  Verify SSD reliability under repeated power cycling in hyperscale conditions.

  Scenario: <REQ_SSD_305> Validate data integrity after 100 power cycles 
    Given a hyperscale SSD with a loaded dataset of 1 TB
    When the operator performs 100 power cycles (cold reboots) on the server
    Then the SSD should always enumerate correctly after each cycle
    And all pre-loaded data should remain intact with no corruption detected
    And SMART logs should not show abnormal error counts
