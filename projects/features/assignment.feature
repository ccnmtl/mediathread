Feature: Assignment

    Scenario: 1. Assignment - Create by test_instructor, verify initial state
        Using selenium
        Given I am test_instructor in Sample Course
        Given there are no projects
        
        # Create an assignment from the home page
        There is a New Composition button
        When I click the New Composition button
        Then I am at the Untitled page
        There is an open Composition panel

        # Add a title and some text
        Then I call the Composition "Assignment: Scenario 1"
        And I write some text for the Composition
        
        # Save as an Assignment
        When I click the Save button
        Then I see a Save Changes dialog
        Then I set the project visibility to "Assignment - published to all students in class, tracks responses"
        When I save the changes
        Then there is an "Assignment" link
        Then there is an open Assignment panel
        
        # Toggle to preview
        When I click the Preview button
        The Assignment panel has a Revisions button
        And the Assignment panel has an Edit button
        And the Assignment panel does not have a Preview button
        And the Assignment panel has a Save button
        And the Assignment panel has a Revisions button
        And the Assignment panel does not have a +/- Author button
        
         # The project shows on Home
        When I click the HOME button
        Then I wait 2 seconds
        Then there is an assignment "Assignment: Scenario 1" project by Instructor One
        Then the instructor panel has 1 projects named "Assignment: Scenario 1"
        
        # View the project - it should appear in "Preview" mode
        When I click the "Assignment: Scenario 1" link
        Then I am at the Assignment: Scenario 1 page
        
        # Preview view elements
        I see "by Instructor One"
        And I see "Assignment: Scenario 1"
        And there is an "Assignment" link
        
        There is an open Assignment panel
        The Assignment panel has a Revisions button
        And the Assignment panel has an Edit button
        And the Assignment panel does not have a Preview button
        And the Assignment panel has a Save button
        And the Assignment panel has a Revisions button
        And the Assignment panel does not have a +/- Author button
        
        # The project shows on Recent Activity
        When I click the Recent Activity button
        Then the most recent notification is "Assignment: Scenario 1"
        
        Finished using Selenium 
        
