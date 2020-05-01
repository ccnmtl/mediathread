Feature: Assignment

    Scenario: assignment.feature 1. Instructor creates assignment
        Using selenium
        Given I am instructor_one in Sample Course

        # Create an assignment from the home page
        I click the Create button
        I click the Create Composition Assignment button 

        Given the assignment workspace is loaded
        Then I am at the Untitled page
        There is an open Assignment panel
        And there is a Saved button
        And there is a "Draft" link

        # Add a title and some text
        Then I call the Assignment "Assignment: Scenario 1"
        Then I write some text for the Assignment
        And there is a Save button

        # Save as an Assignment
        When I click the Save button
        Then I set the project visibility to "Whole Class - all class members can view"
        When I save the project changes
        Then there is an "Published to Class" link
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
        And the Assignment panel does not have an author edit area

        # The project shows on Home
        When I click the "Sample Course" link
        Given the home workspace is loaded
        Then there is an assignment "Assignment: Scenario 1" project by Instructor One

        # View the project - it should appear in "Preview" mode
        When I click the "Assignment: Scenario 1" link
        Given the assignment workspace is loaded
        Then I am at the Assignment: Scenario 1 page

        # Preview view elements
        I see "by Instructor One"
        And I see "Assignment: Scenario 1"
        And there is an "Published to Class" link

        There is an open Assignment panel
        The Assignment panel has a Revisions button
        And the Assignment panel has an Edit button
        And the Assignment panel does not have a Preview button
        And the Assignment panel has a Saved button
        And the Assignment panel has a Revisions button
        And the Assignment panel does not have an author edit area
        And the Assignment panel does not have a Respond To Assignment button
        And the Assignment panel does not have a Responses (1) button

        Finished using Selenium

    Scenario: assignment.feature 2. Student creates assignment response
        Using selenium
        Given there is a sample assignment
        Given I am student_one in Sample Course

        # Respond as a student
        There is an assignment "Sample Assignment" project by Instructor One
        And the instructor panel has 0 projects named "Sample Assignment"
        When I click the "Sample Assignment" link

        Given the assignment workspace is loaded
        Then I am at the Sample Assignment page
        And there is an open Assignment panel
        And the Assignment panel does not have an Edit button
        And the Assignment panel does not have a Preview button
        And the Assignment panel does not have a Saved button
        And the Assignment panel does not have a Revisions button
        And the Assignment panel does not have an author edit area
        And there is not an "Published to Class" link
        And the Assignment panel has a Respond to Assignment button

        # Create the response
        When I click the Respond to Assignment button
        Given the composition workspace is loaded
        Then there is an open Assignment panel
        And there is an open Composition panel
        The Composition panel has a Revisions button
        And the Composition panel has a Preview button
        And the Composition panel does not have an Edit button
        And the Composition panel has a Saved button
        And the Assignment panel does not have an author edit area 

        # Add a title & text
        Then I call the Composition "Sample Assignment Response"

        # Save as submitted to the instructor
        When I click the Save button
        Then I set the project visibility to "Instructor - only author(s) and instructor can view"
        When I save the project changes
        Then there is a "Submitted to Instructor" link

        # Verify home page display
        When I click the "Sample Course" link
        Given the home workspace is loaded
        Then there is a submitted to instructor "Sample Assignment Response" reply by Student One

        Finished using Selenium

    Scenario: assignment.feature 3. Instructor provides response feedback
        Using selenium
        Given there is a sample response
        Given I am instructor_one in Sample Course

        When I select "One, Student" as the owner in the Composition column
        Then the owner is "One, Student" in the Composition column
        Then the composition panel has 1 project named "Sample Assignment"
        Then the composition panel has 1 response named "Sample Assignment Response"

        When I click the "Sample Assignment Response" link

        Given the composition workspace is loaded
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
        Give I am student_one in Sample Course
        Then there is a "Read Instructor Feedback" link
        When I click the "Read Instructor Feedback" link

        Given the composition workspace is loaded
        Then I am at the Sample Assignment Response page
        Then there is an open Discussion panel
        Then there is a comment from "Instructor One"

        Give I am student_two in Sample Course
        When I select "One, Student" as the owner in the Composition column
        Then the owner is "One, Student" in the Composition column
        Then the composition panel has 0 projects named "Sample Assignment Response"
        And there is not a "Read Instructor Feedback" link

        When I select "Two, Student" as the owner in the Composition column
        Then the owner is "Me" in the Composition column

        When I click the "Sample Assignment" link
        Given the assignment workspace is loaded
        Then I am at the Sample Assignment page
        There is an open Assignment panel
        And the Assignment Panel has a Respond to Assignment button
        And the Assignment Panel does not have a Class Responses (1) button

        Finished using Selenium

    Scenario Outline: assignment.feature 4. Assignment Response - visibility rules
        Using selenium
        Given there is a sample assignment
        Give I am student_one in Sample Course

        # This navigates rather than automagically opening the panel
        When I click the Respond to Assignment button

        Given the composition workspace is loaded
        Then I call the Composition "Sample Assignment Response"
        Then I click the Save button
        Then I set the project visibility to "<visibility>"
        When I save the project changes
        Then there is a "<status>" link

        Give I am <username> in Sample Course 
        When I select "One, Student" as the owner in the Composition column
        Then the owner is "One, Student" in the Composition column
        Then the composition panel has <count> responses named "Sample Assignment Response"

        # the response must be deleted
        Given I am student_one in Sample Course
        When I click the "Sample Assignment Response" link
        Given the composition workspace is loaded
        When I click the Saved button
        Then I set the project visibility to "Draft - only you can view"
        Then I save the project changes

        When I click the "Sample Course" link
        Given the home workspace is loaded
        When I click the "Sample Assignment Response" project delete icon
        Then I confirm the action

        Finished using Selenium

      Examples:
        | visibility                                          | status                  | username         | count |
        | Draft - only you can view                           | Draft                   | instructor_one |   0   |
        | Instructor - only author(s) and instructor can view | Submitted to Instructor | instructor_one |   1   |
        | Whole Class - all class members can view            | Published to Class      | instructor_one |   1   |
        | Draft - only you can view                           | Draft                   | student_two |   0   |
        | Instructor - only author(s) and instructor can view | Submitted to Instructor | student_two |   0   |
        | Whole Class - all class members can view            | Published to Class      | student_two |   1   |

    Scenario: assignment.feature 5. Class Responses link - instructor
        Using selenium
        Given there is a sample response
        Give I am instructor_one in Sample Course

        When I click the "Sample Assignment" link
        Given the assignment workspace is loaded
        The Assignment Panel has a Class Responses (1) button

        When I click the Class Responses (1) button
        Then I see a Responses dialog
        When I select Student One's response
        Then I click the View Response button

        Given the composition workspace is loaded
        Then I am at the Sample Assignment Response page
        And the Composition title is "Sample Assignment Response"

        Finished using Selenium

    Scenario: assignment.feature 6. Class Responses link + Response Visibility + Respond - Student Two
        Using selenium
        Given there is a sample response

        # By default, the response is "Instructor Only"
        # Student Two does not have access
        Give I am student_two in Sample Course
        When I click the "Sample Assignment" link
        Given the assignment workspace is loaded
        And the Assignment Panel does not have a Class Responses (1) button

        # Update to "Public to Class" 
        # Student Two can see the button now & view the response
        Given I am student_one in Sample Course
        When I click the "Sample Assignment Response" link
        Given the composition workspace is loaded
        When I click the Saved button
        Then I set the project visibility to "Whole Class - all class members can view"
        When I save the project changes
        Then there is a "Published to Class" link

        # Now, student_two can see the response
        Give I am student_two in Sample Course
        When I click the "Sample Assignment" link
        Given the assignment workspace is loaded
        The Assignment Panel has a Class Responses (1) button

        When I click the Class Responses (1) button
        Then I see a Responses dialog

        When I select Student One's response
        And I click the View Response button
        Given the composition workspace is loaded
        Then I am at the Sample Assignment Response page
        And there is an closed Assignment panel
        And there is an open Composition panel
        And the Composition title is "Sample Assignment Response"

        # Create my own response and make sure it's the right one
        When I toggle the Assignment panel
        Then I click the Respond to Assignment button

        # This navigates rather than automagically opening the panel
        # Save the composition or a warning message appears
        Given the composition workspace is loaded
        Then I am at the Untitled page
        And there is an open Composition panel
        Then I call the Composition "Assignment Response: Scenario 6"
        When I click the Save button
        Then I save the project changes
        Then there is a "Draft" link

        Finished using Selenium

    Scenario: assignment.feature 7. Assignment Response - reset visibility
        Using selenium
        Given there is a sample assignment
        Give I am student_one in Sample Course

        # This navigates rather than automagically opening the panel
        When I click the Respond to Assignment button
        Given the composition workspace is loaded
        Then I call the Composition "Sample Assignment Response"
        Then there is a "Draft" link

        When I click the Save button
        Then I set the project visibility to "Instructor - only author(s) and instructor can view"
        When I save the project changes
        Then there is a "Submitted to Instructor" link

        When I click the Saved button
        Then I set the project visibility to "Whole Class - all class members can view"
        When I save the project changes
        Then there is a "Published to Class" link

        Finished using Selenium
