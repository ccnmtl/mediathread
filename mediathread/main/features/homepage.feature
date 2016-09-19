Feature: Homepage

    Scenario: homepage.feature 1. Instructor default view
        Using selenium
        Given I am instructor_one in Sample Course

        There is a "Course Settings" link

        When I open the reports menu
        Then there is an "Assignment Responses" link
        And there is a "Class Activity" link
        And there is a "Class Member Contributions" link

        And there is a From Your Instructor column
        And there is a Composition column
        And there is a Collection column
        And there is help for the From Your Instructor column
        And there is help for the Composition column
        And there is help for the Collection column

        And there is a Create button
        When I click the Create button
        Then there is a Create Composition Assignment button
        And there is a Create Composition button
        And there is a Create Discussion button

        Finished using Selenium

    Scenario: homepage.feature 2. Student view w/o assignment
        Using selenium
        Given I am student_one in Sample Course

        There is not a "Course Settings" link
        And there is no reports menu

        And there is not a From Your Instructor column
        And there is a Composition column
        And there is a Collection column

        And there is help for the Composition column
        And there is help for the Collection column

        And there is a Create button
        When I click the Create button
        Then there is not a Create Composition Assignment button
        And there is a Create Composition button
        And there is not a Create Discussion button

        Finished using Selenium

    Scenario: homepage.feature 3. Student view w/assignment
        Using selenium
        Given there is a sample assignment
        Given I am student_one in Sample Course

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
        Given I am student_one in Sample Course

        There is not a From Your Instructor column
        The composition panel has 1 projects named "Sample Assignment"
        Then the composition panel has 1 response named "Sample Assignment Response"

        When I click the "Sample Assignment Response" link
        Then I am at the Sample Assignment Response page
        And there is an open Composition panel
        And the Composition title is "Sample Assignment Response" 

        Finished using Selenium


    Scenario Outline: homepage.feature 5. Instructor User Settings menu 
        Using selenium
        Given I am instructor_one in Sample Course
        Given the home workspace is loaded

        When I open the user menu
        Then there is a "Log Out" link
        There is a "My Courses" link
        There is not an "Admin" link

        When I click the "Log Out" link
        Then I am at the Login page 

        Finished using Selenium

    Scenario Outline: homepage.feature 5. Student User Settings menu 
        Using selenium
        Given I am student_one in Sample Course
        Given the home workspace is loaded

        When I open the user menu
        Then there is a "Log Out" link
        There is not a "My Courses" link
        There is not an "Admin" link

        When I click the "Log Out" link
        Then I am at the Login page 

        Finished using Selenium
