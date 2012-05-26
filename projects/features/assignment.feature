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
        And the Assignment panel does not have a Respond To Assignment button
        And the Assignment panel does not have a Responses (1) button
        
        # The project shows on Recent Activity
        When I click the Recent Activity button
        Then the most recent notification is "Assignment: Scenario 1"
        
        Finished using Selenium 
        
    Scenario: 2. Assignment Response - by student, verify creation & initial state
        Using selenium
        Given I am test_instructor in Sample Course
        Given there are no projects
        
        # Create an assignment
        There is a New Composition button
        When I click the New Composition button
        Then I call the Composition "Assignment: Scenario 2"
        And I write some text for the Composition
        
        # Save as an Assignment
        When I click the Save button
        Then I see a Save Changes dialog
        Then I set the project visibility to "Assignment - published to all students in class, tracks responses"
        When I save the changes
        Then there is an "Assignment" link
        Then there is an open Assignment panel
        
        # Respond as a student
        Give I am test_student_one in Sample Course
        There is an assignment "Assignment: Scenario 2" project by Instructor One
        And the instructor panel has 1 project named "Assignment: Scenario 2"
        
        When I click the "Assignment: Scenario 2" link
        Then I am at the Assignment: Scenario 2 page
        And there is an open Assignment panel
        And the Assignment panel does not have an Edit button
        And the Assignment panel does not have a Preview button
        And the Assignment panel does not have a Save button
        And the Assignment panel does not have a Revisions button
        And the Assignment panel does not have a +/- Author button
        And there is not an "Assignment" link
        And the Assignment panel has a Respond to Assignment button
        
        # Create the response
        When I click the Respond to Assignment button
        Then there is an open Assignment panel
        And there is an open Composition panel
        The Composition panel has a Revisions button
        And the Composition panel has a Preview button
        And the Composition panel does not have an Edit button
        And the Composition panel has a Save button
        And the Composition panel has a +/- Author button 
        
        # Add a title & text
        Then I call the Composition "Assignment: Scenario 2 Response"
        And I write some text for the Composition
        
        # Save as submitted to the instructor
        When I click the Save button
        Then I see a Save Changes dialog
        Then I set the project visibility to "Instructor - only author(s) and instructor can view"
        When I save the changes
        Then there is a "Submitted to Instructor" link
        
        # Verify home page display
        When I click the HOME button
        Then I wait 2 seconds
        Then there is a submitted to instructor "Assignment: Scenario 2 Response" project by Student One
        
        # View the project - it should reappear in "Preview" mode
        When I click the "Assignment: Scenario 2 Response" link
        Then I am at the Assignment: Scenario 2 Response page
        
        Then there is an open Assignment panel
        And the Assignment panel does not have an Edit button
        And the Assignment panel does not have a Preview button
        And the Assignment panel does not have a Save button
        And the Assignment panel does not have a Revisions button
        And the Assignment panel does not have a +/- Author button
        And the Assignment panel does not have a Respond to Assignment button
        And there is not an "Assignment" link
        And the Assignment panel has a My Response button
        
        And there is an open Composition panel
        The Composition panel has a Revisions button
        And the Composition panel has an Edit button
        And the Composition panel does not have a Preview button
        And the Composition panel has a Save button
        And the Composition panel has a Revisions button
        And the Composition panel does not have a +/- Author button
        And there is a "Submitted to Instructor" link 
        
        # The project shows on Recent Activity
        When I click the Recent Activity button
        Then the most recent notification is "Assignment: Scenario 2 Response"
        
        Finished using Selenium 
        