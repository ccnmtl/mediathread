Feature: Manage Selection Visibility

    Scenario: manage_selection_visibility.feature 1. Verify default selection visibility is yes
        Using selenium
        Given I am test_instructor in Sample Course
        Given the selection visibility is set to "Yes"
        
        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page
        
        When I click the Manage Course Settings button
        Then I am at the Manage Course Settings page
     
        The selection visibility is "Yes"
        
        Finished using Selenium
        
    Scenario: manage_selection_visibility.feature 2. Change selection visibility to no
        Using selenium
        Given I am test_instructor in Sample Course
        Given the selection visibility is set to "No"
        
        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page
        
        When I click the Manage Course Settings button
        Then I am at the Manage Course Settings page
     
        The selection visibility is "No"
        
        Finished using Selenium        
    
  