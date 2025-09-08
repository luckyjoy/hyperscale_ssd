@manual
Feature: Program PIDs at Member Engine as a user or admin in GW Programming Tool 
- Program PIDs as admin at Cluster Master in Lighting Model

Scenario Outline: Verify Specific Fixture PID Programming in GW Programing Tool as a <User>
    Given a Cluster has several fixtures connected
    #And one fixture is connected to Port=<Port>
    When I visit the Gateway Programming Tool page as a <User>
    Then I should see a message "Redwood Lighting and Sensors control process is active"
    And I should see the button with label text "Disable"
    When I click on the button with label text "Disable"
    Then I should see a text message "Redwood Lighting and Sensor control process is disabled"
    #And I should get a list of all initialized Gateways
    And I should see the Serial_Number=<SN> of an initialized Gateway 
	And I should see the Specific_PIDs=<sPID> of the Gateway with Serial_Number=<SN> 
    And I should see the Port_Number=<Port> of the Gateway with Serial_Numer=<SN>  
    When I click on the button with label "Start Gateway Programming"
    And I click the checkbox next to <Port> 
    And I choose a Fixture Manufacturer from the dropdown field
    And I choose a Fixture Model from the dropdown field
    And I click on the button with label "Apply"
    Then I should see a Confirmation box "Confirm Gateway Programming"
    And I should see the Port_Number=<Port> of the Gateway
    And I should see the Serial_Number=<SN> of the Gateway
    And I should see the Specific_PIDs=<sPID> of the Gateway   #oh no sPID != Fixture_ID
    When I click on the button with label "Confirm"
    And I should see the Port_Number=<Port> of the Gateway
    And I should see the new Serial_Number=<SN> of the Gateway
    And I should see the new Specific_PIDs=<sPID> of the Gateway
    Examples: 
    | 	 Node 	 | User |    sPID    | 		       SN 		       | Port |	
    |memberEngine| user | "ALPD1200" | CFV00000000001J030154901370 | 12   |
    |memberEngine| admin| "AXRL1002" | CFV00000000001J030154901370 | 12   |
    
    
Scenario Outline: Verify Specific Fixture PID Programming in Lighting Model Application 
    Given a Cluster has several Fixtures connected 
    And I am logged into node <node> ad an admin     
    When I visit Lighting Models Application
    Then I should see a list of Fixtures connected to the Cluster
    When I click on the sprocket Icon dropdown
    Then I should see a popup field that reads "Configure Lighting Model"
    When I click on the field "Configure Lighting Model"
    Then I should see a dialog box showing Fixture Model <Vendor - Model> 
    And I should see a warning message about assigning incompatible model type and a checkbox
    When I confirm the checkbox
    And I select a Fixture Model <Vendor - Model> from the dropdown list
    And I click the button with text "Apply"
    Then I should see a throbber animation with text "Pending..."
    When I wait for programming_time = 30 seconds
    Then I should see <sPID> as a text show up unter "Current Model Type"
    When I click the button "Close"
    Then I should see the list of Fixtures connected to the Cluster
    And I should see fixture name <fixture_name> has remained as before
    And I should see the newly programmed Model <Vendor - Model> 
    And I should see fixture name <fixture_name>
    And I should see the Fixture ID <sPID> that corresponds to the newly programmed Model <Vendor - Model>
    
     Examples: 
    | 	 Node 	 |  sPID    |   Vendor - Model                         |    fixture_name             |
    |MasterEngine| BLRW0001 | BetaLED - Essentia 14 Downlight          | 000000000SVS1J0501180800865 |
    |MasterEngine| FRDL1500 | Forma - DL 500mA                         | 000000000SVS1J0501180800865 |

    