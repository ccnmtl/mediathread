Feature: Composition
        
    Scenario: composition.feature 1. Instructor creates composition
        Using selenium
        Given I am test_instructor in Sample Course
        Given there are no projects
        
        # Create a project from the home page
        There is a Create Composition button
        When I click the Create Composition button
        Then I am at the Untitled page
        I see "by Instructor One"
        And I see "Private"
        
        # Verify user is able to edit the project
        There is an open Composition panel
        
        The Composition panel has a Revisions button
        And the Composition panel has a Preview button
        And the Composition panel does not have a Preview button
        And the Composition panel has a Save button
        And the Composition panel has a +/- Author button
        
        # Add a title and some text
        Then I call the Composition "Composition: Scenario 1"
        And I write some text for the Composition
        
        # Save
        When I click the Save button
        Then I see a Save Changes dialog
        There is a project visibility "Private - only author(s) can view"
        There is a project visibility "Assignment - published to all students in class, tracks responses"
        There is a project visibility "Whole Class - all class members can view"
        There is not a project visibility "Whole World - a public url is provided"
        And the project visibility is "Private - only author(s) can view"
        
        Then I save the changes
        Then there is a "Private" link
        
        # Toggle Preview Mode
        When I click the Preview button
        The Composition panel has a Revisions button
        And the Composition panel has an Edit button
        And the Composition panel does not have a Preview button
        And the Composition panel has a Save button
        And the Composition panel has a Revisions button
        And the Composition panel does not have a +/- Author button
        
        # The project shows on Home
        When I click the HOME button
        Then I wait 2 seconds
        Then there is a private "Composition: Scenario 1" project by Instructor One
        
        # View the project - it should appear in "Preview" mode
        When I click the "Composition: Scenario 1" link
        Then I am at the Composition: Scenario 1 page
        
        # Preview view elements
        I see "by Instructor One"
        And I see "Composition: Scenario 1"
        And there is a "Private" link
        
        There is an open Composition panel
        The Composition panel has a Revisions button
        And the Composition panel has an Edit button
        And the Composition panel does not have a Preview button
        And the Composition panel has a Save button
        And the Composition panel has a Revisions button
        And the Composition panel does not have a +/- Author button
        
        # The project shows on View Recent Activity
        When I click the View Recent Activity button
        Then the most recent notification is "Composition: Scenario 1"
        
        Finished using Selenium

    Scenario: composition.feature 2. Student creates composition
        Using selenium
        Given I am test_student_one in Sample Course
        Given there are no projects
        
        # Create a project from the home page
        There is a Create Composition button
        When I click the Create Composition button
        Then I am at the Untitled page
        I see "by Student One"
        And there is a "Private" link
        
        # Verify user is able to edit the project
        There is an open Composition panel
        
        The Composition panel has a Revisions button
        And the Composition panel has a Preview button
        And the Composition panel does not have an Edit button
        And the Composition panel has a Save button
        And the Composition panel has a +/- Author button
        
        # Add a title and some text
        Then I call the Composition "Composition: Scenario 2"
        And I write some text for the Composition
        
        # Save
        When I click the Save button
        Then I see a Save Changes dialog
        There is a project visibility "Private - only author(s) can view"
        There is a project visibility "Instructor - only author(s) and instructor can view"
        There is a project visibility "Whole Class - all class members can view"
        There is not a project visibility "Whole World - a public url is provided"
        There is not a project visibility "Assignment - published to all students in class, tracks responses"
        And the project visibility is "Private - only author(s) can view"
        
        Then I save the changes
        
        # Toggle Preview Mode
        When I click the Preview button
        The Composition panel has a Revisions button
        And the Composition panel has an Edit button
        And the Composition panel does not have a Preview button
        And the Composition panel has a Save button
        And the Composition panel has a Revisions button
        And the Composition panel does not have a +/- Author button
        
        # The project shows on Home
        When I click the HOME button
        Then I wait 2 seconds
        Then there is a private "Composition: Scenario 2" project by Student One
        
        # View the project - it should appear in "Preview" mode
        When I click the "Composition: Scenario 2" link
        Then I am at the Composition: Scenario 2 page
        
        # Preview view elements
        I see "by Student One"
        And I see "Composition: Scenario 2"
        And there is a "Private" link
        
        There is an open Composition panel
        The Composition panel has a Revisions button
        And the Composition panel has an Edit button
        And the Composition panel does not have a Preview button
        And the Composition panel has a Save button
        And the Composition panel has a Revisions button
        And the Composition panel does not have a +/- Author button
        
        # The project shows on View Recent Activity
        When I click the View Recent Activity button
        Then the most recent notification is "Composition: Scenario 2"
        
        Finished using Selenium

    Scenario Outline: composition.feature 3. Composition Visibility - Student Viewing Instructor Created Information / Assignments
        Using selenium
        Given I am test_instructor in Sample Course
                
        # Create a project from the home page
        There is a Create Composition button
        When I click the Create Composition button
        Then I am at the Untitled page
        Then I call the Composition "Composition <title>: Scenario 3"
        
        # Save
        When I click the Save button
        Then I see a Save Changes dialog
        Then I set the project visibility to "<visibility>"
        When I save the changes
        Then there is a "<status>" link
        
        # Try to view as student one
        Given I am test_student_one in Sample Course
        Then the instructor panel has <count> projects named "Composition <title>: Scenario 3"
        
        Finished using Selenium
             
      Examples:
        | title   | visibility                                                        | status             | count |
        | Private | Private - only author(s) can view                                 | Private            | 0     |
        | Assign  | Assignment - published to all students in class, tracks responses | Assignment         | 1     |
        | Public  | Whole Class - all class members can view                          | Published to Class | 1     |
                 
    Scenario Outline: composition.feature 4. Homepage Composition Visibility - Student/Instructor Viewing Another Student's Compositions
        Using selenium
        Given I am test_student_one in Sample Course
                
        # Create a project from the home page
        There is a Create Composition button
        When I click the Create Composition button
        Then I am at the Untitled page
        Then I call the Composition "<title>"
        
        # Save
        When I click the Save button
        Then I see a Save Changes dialog
        Then I set the project visibility to "<visibility>"
        When I save the changes
        Then I see "<status>"
        
        # Try to view as student two
        Given I am test_student_two in Sample Course
        When I select "Student One" as the owner in the Analysis column
        Then the owner is "Student One" in the Analysis column
        Then the classwork panel has <count> projects named "<title>"

        # Try to view as test_instructor
        Given I am test_instructor in Sample Course
        When I select "Student One" as the owner in the Analysis column
        Then the owner is "Student One" in the Analysis column
        Then the classwork panel has <count> projects named "<title>"
        
        Finished using Selenium
             
      Examples:
        | title   | visibility                                      | status             | count |
        | private | Private - only author(s) can view               | Private            | 0     |
        | public  | Whole Class - all class members can view | Published to Class | 1     |


        
        