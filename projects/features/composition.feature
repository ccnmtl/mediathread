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
        And I see "Private - Only Author(s) Can View"
        And I see "Version 1"
        
        # Verify user is able to edit the project
        There is an open Composition panel
        There is an open Collection panel
        
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
        There is a project visibility "Assignment for Class"
        There is a project visibility "Private - Only Author(s) Can View"
        There is a project visibility "Published to Whole Class"
        And the project visibility is "Private - Only Author(s) Can View"
        
        When I save the changes
        Then I see "Version 2"
        
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
        And I see "Private - Only Author(s) Can View"
        And I see "Version 1"
        
        # Verify user is able to edit the project
        There is an open Composition panel
        There is an open Collection panel
        
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
        There is a project visibility "Private - Only Author(s) Can View"
        There is a project visibility "Published to Whole Class"
        And the project visibility is "Private - Only Author(s) Can View"
        
        When I save the changes
        Then I see "Version 2"
        
        # The project shows on Home
        When I click the HOME button
        Then I wait 2 seconds
        Then there is a private "Composition: Scenario 2" project by Student One
        
        # The project shows on Recent Activity
        When I click the Recent Activity button
        Then the most recent notification is "Composition: Scenario 2"
        
        Finished using Selenium

    Scenario Outline: 3. Composition Visibility - Private
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
        Then I save the changes
        
        # Try to view as student one
        When I log out
        When I type "test_student_one" for username
        When I type "test" for password
        When I click the Log In button
        Then I am at the Home page
        Then there are "<count>" projects named "<title">
             
      Examples:
        | title   | visibility                        | count |
        | private | Private - Only Author(s) Can View |   0   |
        | public  | Published to Whole Class          |   1   |        
        