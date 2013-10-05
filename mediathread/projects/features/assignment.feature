Feature: Assignment

    Scenario: assignment.feature 1. Instructor creates assignment
        Using selenium
        Given I am test_instructor in Sample Course
        Given there are no projects
        
        # Create an assignment from the home page
        There is a Create button
        When I click the Create button
        Then there is a Create Assignment button
        And there is a Create Composition button
        And there is a Create Discussion button
        
        When I click the Create Composition button       
        
        Then I am at the Untitled page
        There is an open Composition panel
        And there is a Saved button

        # Add a title and some text
        Then I call the Composition "Assignment: Scenario 1"
        And there is a Save button
        And I write some text for the Composition
        
        # Save as an Assignment
        When I click the Save button
        Then I see a Save Changes dialog
        Then I set the project visibility to "Assignment - published to all students in class, tracks responses"
        When I save the changes
        Then there is an "Assignment" link
        Then there is an open Assignment panel
        And the composition "Assignment: Scenario 1" has text 
        And there is a Saved button       
        
        # Toggle to preview
        When I click the Preview button
        The Assignment panel has a Revisions button
        And the Assignment panel has an Edit button
        And the Assignment panel does not have a Preview button
        And the Assignment panel has a Saved button
        And the Assignment panel has a Revisions button
        And the Assignment panel does not have a +/- Author button
        
         # The project shows on Home
        When I click the "Sample Course" link
        Given the home workspace is loaded
        Then there is an assignment "Assignment: Scenario 1" project by Instructor One
        
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
        And the Assignment panel has a Saved button
        And the Assignment panel has a Revisions button
        And the Assignment panel does not have a +/- Author button
        And the Assignment panel does not have a Respond To Assignment button
        And the Assignment panel does not have a Responses (1) button
        
        Finished using Selenium 
        
    Scenario: assignment.feature 2. Student creates assignment response
        Using selenium
        Given there is a sample assignment
        Given I am test_student_one in Sample Course
        
        # Respond as a student
        There is an assignment "Sample Assignment" project by Instructor One
        And the instructor panel has 0 projects named "Sample Assignment"
        
        When I click the "Sample Assignment" link
        Then I am at the Sample Assignment page
        And there is an open Assignment panel
        And the Assignment panel does not have an Edit button
        And the Assignment panel does not have a Preview button
        And the Assignment panel does not have a Saved button
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
        And the Composition panel has a Saved button
        And the Composition panel has a +/- Author button 
        
        # Add a title & text
        Then I call the Composition "Sample Assignment Response"
        
        # Save as submitted to the instructor
        When I click the Save button
        Then I see a Save Changes dialog
        Then I set the project visibility to "Instructor - only author(s) and instructor can view"
        When I save the changes
        Then there is a "Submitted to Instructor" link
        
        # Verify home page display
        When I click the "Sample Course" link
        Given the home workspace is loaded
        Then there is a submitted to instructor "Sample Assignment Response" reply by Student One

    Scenario: assignment.feature 3. Instructor provides response feedback
        Using selenium
        Given there is a sample response
        Given I am test_instructor in Sample Course
        
        When I select "Student One" as the owner in the Composition column
        Then the owner is "Student One" in the Composition column
        Then the composition panel has 1 project named "Sample Assignment"
        Then the composition panel has 1 response named "Sample Assignment Response"
        
        When I click the "Sample Assignment Response" link
        Then I am at the Sample Assignment Response page
        
        There is an closed Assignment panel
        
        There is an open Composition panel
        And the Composition Panel does not have a Revisions button
        And the Composition Panel does not have an Edit button
        And the Composition Panel does not have a Save button
        And the Composition Panel has a Create Instructor Feedback button
        And there is not a "Submitted to Instructor" link

        There is not an open Discussion panel
        There is not a closed Discussion panel
        
        # Create Instructor Feedback
        When I click the Create Instructor Feedback button
        Then there is an open Discussion panel        
        Then I write some text for the discussion
        Then I click the Save Comment button
        Then there is a comment from "Instructor One"
        
        # View as Student One
        Give I am test_student_one in Sample Course
        Then there is a "Read Instructor Feedback" link
        When I click the "Read Instructor Feedback" link
        
        Then I am at the Sample Assignment Response page
        Then there is an open Discussion panel
        Then there is a comment from "Instructor One"
        
        Give I am test_student_two in Sample Course
        When I select "Student One" as the owner in the Composition column
        Then the owner is "Student One" in the Composition column
        Then the composition panel has 0 projects named "Sample Assignment Response"
        And there is not a "Read Instructor Feedback" link
        
        When I select "Student Two" as the owner in the Composition column
        Then the owner is "Me" in the Composition column
        
        When I click the "Sample Assignment" link
        Then I am at the Sample Assignment page
        There is an open Assignment panel
        And the Assignment Panel has a Respond to Assignment button
        And the Assignment Panel does not have a Class Responses (1) button

        Finished using Selenium
        
    Scenario Outline: assignment.feature 4. Assignment Response - visibility rules        
        Using selenium
        Given there is a sample response
        Give I am test_student_one in Sample Course
        
        # Set the assignment response visibility
        When I click the "Sample Assignment Response" link
        Then I am at the Sample Assignment Response page
        
        Then there is a closed Assignment panel
        And there is an open Composition panel
        
        The Composition panel has a Revisions button
        And the Composition panel has an Edit button
        And the Composition panel does not have a Preview button
        And the Composition panel has a Saved button
        And the Composition panel has a Revisions button
        And the Composition panel does not have a +/- Author button
        And there is a "Submitted to Instructor" link 
        
        When I click the Saved button
        Then I see a Save Changes dialog
        Then I set the project visibility to "<visibility>"
        When I save the changes
        Then there is a "<status>" link
        
        Give I am <username> in Sample Course 
        When I select "Student One" as the owner in the Composition column
        Then the owner is "Student One" in the Composition column
        Then the composition panel has <count> responses named "Sample Assignment Response"
        
        Finished using Selenium
             
      Examples:
        | visibility                                          | status                  | username         | count |
        | Private - only author(s) can view                   | Private                 | test_instructor  |   0   |
        | Instructor - only author(s) and instructor can view | Submitted to Instructor | test_instructor  |   1   |
        | Whole Class - all class members can view            | Published to Class      | test_instructor  |   1   |
        | Private - only author(s) can view                   | Private                 | test_student_two |   0   |
        | Instructor - only author(s) and instructor can view | Submitted to Instructor | test_student_two |   0   |
        | Whole Class - all class members can view            | Published to Class      | test_student_two |   1   |

    Scenario: assignment.feature 5. Class Responses link - instructor       
        Using selenium
        Given there is a sample response
        Give I am test_instructor in Sample Course
        
        When I click the "Sample Assignment" link
        Then I am at the Sample Assignment page
        There is an open Assignment panel
        And the Assignment Panel has a Class Responses (1) button
        
        When I click the Class Responses (1) button
        Then I see a Responses dialog
        When I select Student One's response
        Then I click the View Response button
        
        Then I am at the Sample Assignment Response page
        And there is an closed Assignment panel
        And there is an open Composition panel
        And the Composition title is "Sample Assignment Response"
        
        Finished using Selenium
        
    Scenario: assignment.feature 6. Class Responses link + Response Visibility + Respond - Student Two       
        Using selenium
        Given there is a sample response
        
        # By default, the response is "Instructor Only"
        # Student Two does not have access
        Give I am test_student_two in Sample Course
        When I click the "Sample Assignment" link
        Then I am at the Sample Assignment page
        There is an open Assignment panel
        And the Assignment Panel has a Respond to Assignment button
        And the Assignment Panel does not have a Class Responses (1) button

        # Update to "Public to Class" 
        # Student Two can see the button now & view the response       
        Given I am test_student_one in Sample Course
        When I click the "Sample Assignment Response" link
        Then I am at the Sample Assignment Response page
        Then there is an open Composition panel
        When I click the Saved button
        Then I see a Save Changes dialog
        Then I set the project visibility to "Whole Class - all class members can view"
        When I save the changes
        Then there is a "Published to Class" link
        
        # Now, test_student_two can see the response
        Give I am test_student_two in Sample Course
        When I click the "Sample Assignment" link
        Then I am at the Sample Assignment page
        There is an open Assignment panel
        And the Assignment Panel has a Class Responses (1) button
        And the Assignment Panel has a Respond to Assignment button

        When I click the Class Responses (1) button
        Then I see a Responses dialog
        
        When I select Student One's response
        And I click the View Response button
        Then I am at the Sample Assignment Response page
        And there is an closed Assignment panel
        And there is an open Composition panel
        And the Composition title is "Sample Assignment Response"
        
        # Create my own response and make sure it's the right one
	    When I toggle the Assignment panel
        Then I click the Respond to Assignment button
        
        # This navigates rather than automagically opening the panel
        Given the composition workspace is loaded

        Then I am at the Untitled page
        And there is an open Composition panel
        The Composition panel has a Revisions button
        And the Composition panel has a Preview button
        And the Composition panel does not have an Edit button
        And the Composition panel has a Saved button
        And the Composition panel has a +/- Author button
        
        Then I call the Composition "Assignment Response: Scenario 6"
        When I click the Save button
        Then I see a Save Changes dialog
        Then I save the changes        
        Then there is a "Private" link
        
        When I log out
        Then I am at the Login page
        
        Finished using Selenium
