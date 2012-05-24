Feature: Composition
        
    Scenario: 1. Composition - create by test_instructor
        Using selenium
        Given I am test_instructor in Sample Course
        Given there are no projects
        
        # Create a project from the home page
        There is a New Composition button
        When I click the New Composition button
        Then I am at the Untitled page
        I see "by Instructor One"
        And I see "Private"
        
        # Verify user is able to edit the project
        There is an open Composition panel
        
        The Composition panel has a Revisions button
        And the Composition panel has a Preview button
        And the Composition panel has a Save button
        And the Composition panel has a +/- Author button
        
        # Add a title and some text
        Then I call the Composition "Composition: Scenario 1"
        And I write some text for the Composition
        
        # Save
        When I click the Save button
        Then I see a Save Changes dialog
        There is a project visibility "Private - only author(s) can view"
        There is a project visibility "Assignment - work for all class members"
        There is a project visibility "Whole Class - information for all class members"
        There is not a project visibility "Whole World - a public url is provided"
        And the project visibility is "Private - only author(s) can view"
        
        When I save the changes
        
        # The project shows on Home
        When I click the HOME button
        Then I wait 2 seconds
        Then there is a private "Composition: Scenario 1" project by Instructor One
        
        # The project shows on Recent Activity
        When I click the Recent Activity button
        Then the most recent notification is "Composition: Scenario 1"
        
        Finished using Selenium

    Scenario: 2. Composition - create by test_student_one
        Using selenium
        Given I am test_student_one in Sample Course
        Given there are no projects
        
        # Create a project from the home page
        There is a New Composition button
        When I click the New Composition button
        Then I am at the Untitled page
        I see "by Student One"
        And I see "Private"
        
        # Verify user is able to edit the project
        There is an open Composition panel
        
        The Composition panel has a Revisions button
        And the Composition panel has a Preview button
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
        There is a project visibility "Whole Class - information for all class members"
        There is not a project visibility "Whole World - a public url is provided"
        And the project visibility is "Private - only author(s) can view"
        
        When I save the changes
        
        # The project shows on Home
        When I click the HOME button
        Then I wait 2 seconds
        Then there is a private "Composition: Scenario 2" project by Student One
        
        # The project shows on Recent Activity
        When I click the Recent Activity button
        Then the most recent notification is "Composition: Scenario 2"
        
        Finished using Selenium

    Scenario Outline: 3. Homepage Composition Visibility - Student Viewing Instructor Created Information / Assignments
        Using selenium
        Given I am test_instructor in Sample Course
                
        # Create a project from the home page
        There is a New Composition button
        When I click the New Composition button
        Then I am at the Untitled page
        Then I call the Composition "<title>"
        
        # Save
        When I click the Save button
        Then I see a Save Changes dialog
        Then I set the project visibility to "<visibility>"
        When I save the changes
        Then I see "<status>"
        
        # Try to view as student one
        Given I am test_student_one in Sample Course
        Then the instructor panel has <count> projects named "<title>"
        
        Finished using Selenium
             
      Examples:
        | title   | visibility                                      | status             | count |
        | private | Private - only author(s) can view               | Private            | 0     |
        | assign  | Assignment - work for all class members         | Assignment         | 1     |
        | public  | Whole Class - information for all class members | Published to Class | 1     |
                 
    Scenario Outline: 4. Homepage Composition Visibility - Student/Instructor Viewing Another Student's Compositions
        Using selenium
        Given I am test_student_one in Sample Course
                
        # Create a project from the home page
        There is a New Composition button
        When I click the New Composition button
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
        | public  | Whole Class - information for all class members | Published to Class | 1     |

            
        