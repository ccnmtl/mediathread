Feature: Instructor Dashboard

    Scenario: instructor_dashboard.feature 1. Students are forbidden
        Using selenium
        Given I am test_student_one in Sample Course
        
        # Instructor Dashboard
        When I access the url "/dashboard/"
        Then I do not see "Instructor Dashboard"
        And I see "forbidden"
        
        # Manage Sources
        When I access the url "/dashboard/addsource/"
        Then I do not see "Manage Sources"
        And I see "forbidden"
        
        # Publishing Settings
        When I access the url "/dashboard/settings/"
        Then I do not see "Manage Settings"
        And I see "forbidden"
        
        # Reports
        When I access the url "/reports/class_assignments/"
        Then I do not see "Assignment Responses"
        And I see "forbidden"
        
        When I access the url "/reports/class_activity/"
        Then I do not see "Class Activity"
        And I see "forbidden"
        
        When I access the url "/reports/class_summary/"
        Then I do not see "Student Contributions"
        And I see "forbidden"
               
        Finished using Selenium
        
    Scenario: instructor_dashboard.feature 2. Verify expected instructor functionality
        Using selenium
        Given I am test_instructor in Sample Course
        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page
        And there is a Manage Sources button
        And there is a Manage Course Settings button
        And there is a Create Composition or Assignment button
        And there is a Create Discussion button
        And there is an Assignment Responses button
        And there is a Class Activity button
        And there is a Student Contributions button
        Finished using Selenium
        
    Scenario: instructor_dashboard.feature 3. Class Activity      
        Using selenium
        Given there is a sample assignment and response
        Given I am test_instructor in Sample Course
        
        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page
        When I click the Class Activity button
        Then I see "Report: Class Activity"
        
        And there is a "MAAP Award Reception" link
        And there is a "Sample Assignment Response" link
        And there is a "The Armory - Home to CCNMTL'S CUMC Office" link
        And there is a "Mediathread: Introduction" link
            
        Finished using Selenium
        
    Scenario: instructor_dashboard.feature 4. Test Create Discussion
        Using selenium
        Given there is a sample assignment and response
        Given I am test_instructor in Sample Course
        
        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page
        When I click the Create Discussion button
        Then I am at the Discussion page
        When I click the HOME button
        Then I am at the Home page
        And there is a "Discussion Title" link
        When I click the "Discussion Title" link
        Then I am at the Discussion page
        
        Finished using Selenium
        
    Scenario: instructor_dashboard.feature 5. Test Create Composition
        Using selenium
        Given there is a sample assignment and response
        Given I am test_instructor in Sample Course
        
        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page
        When I click the Create Composition or Assignment button
        Then I am at the Untitled page
        
        There is an open Composition panel
        I call the Composition "Instructor Dashboard: Scenario 4"
        And I write some text for the Composition
        Then I click the Save button
        And I save the changes
        
        When I click the HOME button
        Then I am at the Home page
        Then there is a private "Instructor Dashboard: Scenario 4" project by Instructor One
        
        Finished using Selenium
        
    Scenario: instructor_dashboard.feature 6. Test Assignment Responses      
        Using selenium
        Given there is a sample assignment and response
        Given I am test_instructor in Sample Course
        
        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page        
        When I click the Assignment Responses button
        There is a "Sample Assignment" link
        When I click the "Sample Assignment" link
        Then I am at the Sample Assignment page
        There is an open Assignment panel

        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page        
        When I click the Assignment Responses button        
        Then there is a "1 / 5" link
        When I click the "1 / 5" link
        Then I see "Assignment Report: Sample Assignment"
        And I see "Student One"
        And I there is a "Sample Assignment Response" link
        And I see "Submitted to Instructor"
        And I see "No feedback" 
        
        When I click the "Sample Assignment Response" link
        Then I am at the Sample Assignment Response page
        There is an open Composition panel
        And the Composition title is "Sample Assignment Response"
         
        Finished using Selenium
        
    Scenario: instructor_dashboard.feature 7. Student Contributions     
        Using selenium
        Given there is a sample assignment and response
        Given I am test_instructor in Sample Course
        
        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page
        When I click the Student Contributions button
        Then I see "Report: Student Contributions"
        
        Finished using Selenium  