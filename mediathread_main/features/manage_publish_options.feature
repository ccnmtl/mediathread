Feature: Manage Sources

    Scenario: manage_publish_options.feature 1. Publish options - default is off
        Using selenium
        Given I am test_instructor in Sample Course
        
        When I open the tools menu
        Then there is a "Manage Settings" link
        When I click the "Manage Settings" link
        Then I am at the Manage Course Settings page
     
        Then publish to world is disabled
        
        Finished using Selenium

    Scenario: manage_publish_options.feature 2. Publish options set to Yes
        Using selenium
        Given I am test_instructor in Sample Course
        Given publish to world is enabled
        
        When I open the tools menu
        Then there is a "Manage Settings" link
        When I click the "Manage Settings" link
        Then I am at the Manage Course Settings page
     
        Then publish to world is enabled
        
        Finished using Selenium
        
    Scenario: manage_publish_options.feature 3. Publish options set to No
        Using selenium
        Given I am test_instructor in Sample Course
        Given publish to world is disabled
        
        When I open the tools menu
        Then there is a "Manage Settings" link
        When I click the "Manage Settings" link
        Then I am at the Manage Course Settings page
             
        Then publish to world is disabled
        
        Finished using Selenium        
    
  