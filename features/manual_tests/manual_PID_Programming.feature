@manual @manPIDProgramming
Feature: Program PIDs as admin at <Node> in Lighting Model
    
Scenario Outline: Verify Specific Fixture PID Programming in Lighting Model Application 
    Given a Cluster has several Fixtures connected 
    And I am logged into node <node> as an admin     
    When I visit Lighting Models Application
    Then I should see a list of Fixtures connected to the Cluster
    When I click on the sprocket Icon dropdown
    Then I should see a popup field that reads "Configure Lighting Model"
    When I click on the field "Configure Lighting Model"
    Then I should see a dialog box showing Fixture Model <Vendor - Model> 
    And I should see a warning message about assigning incompatible model type and a checkbox
    When I confirm the checkbox
    And I select a Fixture Model <Vendor - Model> from the dropdown list
    And I click the button "Apply"
    Then I should see a throbber animation "Pending..."
    When I wait for programming_time = 30 seconds
    Then I should see <sPID> as a text show up unter "Current Model Type"
    When I click the button "Close"
    Then I should see the list of Fixtures connected to the Cluster
    And I should see fixture name <fixture_name> has remained as before
    And I should see the newly programmed Model <Vendor - Model> 
    And I should see fixture name <fixture_name>
    And I should see the Fixture_ID=<sPID> that corresponds to the newly programmed Model <Vendor - Model>
    
     Examples: 
    | 	 Node 	   |  sPID    |   Vendor - Model                         |    fixture_name             |
    |"MasterEngine"| BLRW0001 | BetaLED - Essentia 14 Downlight          | 000000000SVS1J0501180800865 |
    |"MasterEngine"| FRDL1500 | Forma - DL 500mA                         | 000000000SVS1J0501180800865 |
    | "Director"   | GNEW1500 | wtec - Generic 500-700                   | 000000000SVS1J0501180800865 |
    | "Director"   | GNRC1500 | wtec - 3G PID 500-679                    | 000000000SVS1J0501180800865 |
 
   
   
   
   
   
   
    
    
    
    
