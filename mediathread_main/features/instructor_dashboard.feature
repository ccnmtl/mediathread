Feature: Instructor Dashboard

    Scenario: 1. Students are forbidden
        Using selenium
        Given I am logged in as test_student_one
        Given I am in the Sample Course class
        
        # Instructor Dashboard
        When I access the url "/dashboard/"
        Then I do not see "Instructor Dashboard"
        Then I see "forbidden"
        
        # Manage Sources
        When I access the url "/dashboard/addsource/"
        Then I do not see "Manage Sources"
        Then I see "forbidden"
        
        # Publishing Settings
        When I access the url "/dashboard/settings/"
        Then I do not see "Manage Settings"
        Then I see "forbidden"
        
        # Reports
        When I access the url "/reports/class_assignments/"
        Then I do not see "Assignment Responses"
        Then I see "forbidden"
        
        When I access the url "/reports/class_activity/"
        Then I do not see "Class Activity"
        Then I see "forbidden"
        
        When I access the url "/reports/class_summary/"
        Then I do not see "Student Contributions"
        Then I see "forbidden"
               
        Finished using Selenium
        
    Scenario: 2. Instructor functionality exists
        Using selenium
        Given I am logged in as test_instructor
        Given I am in the Sample Course class
        When I access the url "/"
        Then I am at the Home page
        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page
        There is a Manage Sources button
        There is a Manage Publishing Options button
        There is a Create Composition Or Assignment button
        There is a Create Discussion button
        There is an Assignment Responses button
        There is a Class Activity button
        There is a Student Contributions button
        Finished using Selenium     
        
    Scenario: 3. Manage Publishing Settings
        Using selenium
        Given I am logged in as test_instructor
        Given I am in the Sample Course class
        When I access the url "/dashboard/"
        Then I am at the Instructor Dashboard page
        When I click the Manage Publishing Options button
        Then I am at the Manage Publishing Options page
        ## TODO
        Finished using Selenium
        
    Scenario: 4. Create Composition or Assignment
        Using selenium
        Given I am logged in as test_instructor
        Given I am in the Sample Course class
        When I access the url "/dashboard/"
        Then I am at the Instructor Dashboard page
        When I click the Create Composition Or Assignment button
        Then I am at the Untitled page
        When I click the HOME button
        Then I dismiss a save warning
        Then I am at the Home page
        Finished using Selenium
        
    Scenario: 5. Create Discussion
        Using selenium
        Given I am logged in as test_instructor
        Given I am in the Sample Course class
        When I access the url "/dashboard/"
        Then I am at the Instructor Dashboard page
        When I click the Create Discussion button
        Then I am at the Discussion page
        When I click the HOME button
        Then I am at the Home page
        Finished using Selenium