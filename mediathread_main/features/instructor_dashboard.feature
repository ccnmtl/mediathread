Feature: Instructor Dashboard

    Scenario: 1. Instructor Dashboard - Students are forbidden
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
        
    Scenario: 2. Instructor Dashboard - Verify expected instructor functionality
        Using selenium
        Given I am test_instructor in Sample Course
        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page
        And there is a Manage Sources button
        And there is a Manage Course Settings button
        And there is a Create Composition Or Assignment button
        And there is a Create Discussion button
        And there is an Assignment Responses button
        And there is a Class Activity button
        And there is a Student Contributions button
        Finished using Selenium     
        
    Scenario: 4. Instructor Dashboard - Test Create Discussion
        Using selenium
        Given I am test_instructor in Sample Course
        
        When I access the url "/dashboard/"
        Then I am at the Instructor Dashboard page
        When I click the Create Discussion button
        Then I am at the Discussion page
        When I click the HOME button
        Then I am at the Home page
        Finished using Selenium