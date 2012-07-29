Feature: Manage Sources
    
    Scenario: 1. Instructor Dashboard - Test Manage Publishing Settings
        Using selenium
        Given I am test_instructor in Sample Course
        
        When I access the url "/dashboard/"
        Then I am at the Instructor Dashboard page
        When I click the Manage Course Settings button
        Then I am at the Manage Course Settings page
        ## TODO
        Finished using Selenium