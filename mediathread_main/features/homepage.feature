Feature: Homepage

    Scenario: homepage.feature 1. Instructor default view
        Using selenium
        Given I am test_instructor in Sample Course
        
        When I open the tools menu
        Then there is a "Manage Settings" link
        Then there is a "Manage Sources" link
        Then there is a "Migrate Materials" link
        
        When I open the reports menu
        Then there is an "Assignment Responses" link
        And there is a "Class Activity" link
        And there is a "Student Contributions" link
                
        And there is a From Your Instructor column
        And there is a Composition column
        And there is a Collection column
        And there is help for the From Your Instructor column
        And there is help for the Composition column
        And there is help for the Collection column
        
        Finished using Selenium
        
    Scenario: homepage.feature 2. Student view w/o assignment
        Using selenium
        Given I am test_student_one in Sample Course
        Then there is no tools menu
        And there is no reports menu
        
        And there is not a From Your Instructor column
        And there is a Composition column
        And there is a Collection column
        
        And there is help for the Composition column
        And there is help for the Collection column
        
        Finished using Selenium

    Scenario: homepage.feature 3. Student view w/assignment
        Using selenium
        Given there is a sample assignment
        Given I am test_student_one in Sample Course
        
        And there is not a From Your Instructor column
        Then the composition panel has 1 projects named "Sample Assignment"
        
        And there is a Composition column
        And there is a Collection column
        
        And there is help for the Composition column
        And there is help for the Collection column
        
        When I click the "Sample Assignment" link
        Then I am at the Sample Assignment page
        And there is an open Assignment panel
        And the Assignment title is "Sample Assignment"
        
        Finished using Selenium
        
    Scenario: homepage.feature 4. Student view w/assignment & response
        Using selenium
        Given there is a sample response
        Given I am test_student_one in Sample Course
        
        There is not a From Your Instructor column
        The composition panel has 1 projects named "Sample Assignment"
        Then the composition panel has 1 response named "Sample Assignment Response"
        
        When I click the "Sample Assignment Response" link
        Then I am at the Sample Assignment Response page
        And there is an open Composition panel
        And the Composition title is "Sample Assignment Response"  
        
        Finished using Selenium   
        
        
    Scenario Outline: homepage.feature 5. User Settings menu
        Using selenium
        Given I am <user_name> in Sample Course
        
        When I open the user menu
        Then there is a "Log Out" link
        There is not a "Switch Course" link
        There is not an "Admin" link
        
        When I click the "Log Out" link
        Then I am at the Login page 

        Finished using Selenium
        
    Examples:
        | user_name           |
        | test_instructor     |
        | test_student_one    |         
                

        
        
        
         