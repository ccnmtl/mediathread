Feature: Manage Sources

    Scenario: 1. Manage Publish Options - Default is off
        Using selenium
        Given I am test_instructor in Sample Course
        
        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page
        
        When I click the Manage Course Settings button
        Then I am at the Manage Course Settings page
     
        Then publish to world is disabled
        
        Finished using Selenium

    Scenario: 2. Manage Publish Options - Yes
        Using selenium
        Given I am test_instructor in Sample Course
        Given publish to world is enabled
        
        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page
        
        When I click the Manage Course Settings button
        Then I am at the Manage Course Settings page
     
        Then publish to world is enabled
        
        Finished using Selenium
        
    Scenario: 3. Manage Publish Options - No
        Using selenium
        Given I am test_instructor in Sample Course
        Given publish to world is disabled
        
        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page
        
        When I click the Manage Course Settings button
        Then I am at the Manage Course Settings page
     
        Then publish to world is disabled
        
        Finished using Selenium        
    
  