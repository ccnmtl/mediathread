Feature: Instructor Dashboard

    Scenario: instructor_dashboard.feature 1. Students are forbidden
        Using selenium
        Given I am student_one in Sample Course
        
        # No Instructor Menus
        Then I am at the Home page
        There is no manage menu
        There is no reports menu
        
        # Manage Sources
        When I access the url "/dashboard/sources/"
        Then I do not see "Manage Sources"
        And I see "forbidden"
        
        # Publishing Settings
        When I access the url "/dashboard/settings/"
        Then I do not see "Manage Settings"
        And I see "forbidden"

        # Taxonomy
        When I access the url "/taxonomy/"
        Then I do not see "Course Vocabulary"
        And I see "forbidden"

        # Reports
        When I access the url "/reports/class_assignments/"
        Then I do not see "Assignment Responses"
        And I see "forbidden"
        
        When I access the url "/reports/class_activity/"
        Then I do not see "Class Activity"
        And I see "forbidden"
        
        When I access the url "/reports/class_summary/"
        Then I do not see "Class Member Contributions"
        And I see "forbidden"
               
        Finished using Selenium
                
    Scenario: instructor_dashboard.feature 2. Class Activity      
        Using selenium
        Given there is a sample response
        Given there are sample assets
        Given I am instructor_one in Sample Course
        
        When I open the reports menu
        There is a "Class Activity" link
        When I click the "Class Activity" link
        Then I see "Report: Class Activity"
        
        And there is a "MAAP Award Reception" link
        And there is a "Sample Assignment Response" link
        And there is a "The Armory - Home to CCNMTL's CUMC Office" link
        And there is a "Mediathread: Introduction" link
            
        Finished using Selenium
        
    Scenario: instructor_dashboard.feature 3. Test Create Discussion
        Using selenium
        Given there is a sample response
        Given I am instructor_one in Sample Course
        
        There is a Create button
        When I click the Create button
        
        When I click the Create Discussion button
        Then I am at the Discussion page
        When I click the "Sample Course" link
        Given the home workspace is loaded
        There is a "Discussion Title" link
        When I click the "Discussion Title" link
        Then I am at the Discussion page
        
        Finished using Selenium
        
    Scenario: instructor_dashboard.feature 4. Test Create Composition
        Using selenium
        Given there is a sample response
        Given I am instructor_one in Sample Course
        
        There is a Create button
        When I click the Create button
        When I click the Create Composition button
        
        Then I am at the Untitled page
        
        There is an open Composition panel
        I call the Composition "Instructor Feature 4"
        Then the Composition is called "Instructor Feature 4"
        Then I click the Save button
        And I save the changes
        Then the Composition is called "Instructor Feature 4"
        
        When I click the "Sample Course" link
        Given the home workspace is loaded
        Then there is a draft "Instructor Feature 4" project by Instructor One
        
        Finished using Selenium
        
    Scenario: instructor_dashboard.feature 5. Test Assignment Responses      
        Using selenium
        Given there is a sample response
        Given I am instructor_one in Sample Course

        When I open the reports menu
        When I click the "Assignment Responses" link
        Then there is a "1 / 3" link
        When I click the "1 / 3" link
        Then I see "Assignment Report: Sample Assignment"
        And I see "Student One"
        And I there is a "Sample Assignment Response" link
        And I see "Submitted to Instructor"
        And I see "No"

        When I click the "Sample Assignment Response" link
        Then I am at the Sample Assignment Response page
        There is an open Composition panel
        And the Composition title is "Sample Assignment Response"

        Finished using Selenium
        
    Scenario: instructor_dashboard.feature 6. Student Contributions     
        Using selenium
        Given there is a sample response
        Given I am instructor_one in Sample Course
        
        When I open the reports menu
        When I click the "Class Member Contributions" link
        Then I see "Report: Class Member Contributions"
        
        Finished using Selenium  