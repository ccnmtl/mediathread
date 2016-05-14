Feature: Selection Assignment

    Scenario: selectionassignment.feature 1. Instructor creates assignment
        Using selenium
        Given there are sample assets
        Given I am instructor_one in Sample Course

        # Create an assignment from the home page
        I click the Create button
        I click the Create Selection Assignment button 

        Then I am at the Create Assignment page
        I click the Get Started button
        Then I see "Choose an item from the course collection"
        I click the Next button
        Then I see "An item must be selected"
        I click a gallery item
        I click the Next button
        Then I see "Write title"
        I click the Next button
        Then I see "Title is a required field"
        And I see "Instructions is a required field"
        I call the selection assignment "Test Selection Assignment"
        I write instructions for the selection assignment
        I click the Next button
        Then I see "Set response due date"
        I click the Next button
        Then I see "Please choose a due date"
        Then I see "Please choose how responses will be viewed"
        I set selection assignment visibility to "never"
        I set selection assignment due date
        I click the Next button
        Then I see "Publish assignment to students"
        I click the Save button
        Then I see "Please select who can see your work"
        I publish the selection assignment as "Whole Class"
        I click the Save button
        
        Then I am at the Test Selection Assignment page 
        
        Finished using Selenium

    Scenario: selectionassignment.feature 2. Student responds to assignment
        Using selenium
        Given there is a sample selection assignment
        Given I am student_one in Sample Course

        There is an assignment "Sample Selection Assignment" project by Instructor One

        When I click the Respond to Assignment button
        Then I am at the Sample Selection Assignment page
        
        I click the Create a selection button
        And there is a Save Selection button
        I click the Save Selection button

        I'm told "Please specify a selection title"
        I confirm the action

        I type "Foo" for annotation-title
        I click the Save Selection button
        I click the Submit Response button
        I submit the selection assignment

        Then I see "Submitted"
        And there is not a Submit Response button
        
        Finished using Selenium
   
    Scenario: selectionassignment.feature 3. Instructor adds and edits feedback
        Using selenium
        Given there is a sample selection assignment and response
        Given I am instructor_one in Sample Course

        When I select "Student One" as the owner in the Composition column
        Then the owner is "Student One" in the Composition column
        Then the composition panel has 1 project named "Sample Selection Assignment"
        Then the composition panel has 1 response named "My Response"

        When I click the "Sample Selection Assignment" link
        Then I am at the Sample Selection Assignment page
        
        I see "1 Responses"
        The feedback count is 0
        
        I click the "add feedback" link
        I add some feedback to the selection assignment response
        I click the Save Feedback button

        There is an "edit feedback" link
        The feedback count is 1

        Finished using Selenium
