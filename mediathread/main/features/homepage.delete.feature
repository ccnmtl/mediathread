Feature: Homepage Delete Operations. Project, Item

    Scenario: homepage.delete.feature 1. Student cannot delete assignment
        Using selenium
        Given there is a sample assignment
        Given I am test_student_one in Sample Course
        
        Given the home workspace is loaded
        The "Sample Assignment" project has no delete icon

        Finished using Selenium 
        
    Scenario: homepage.delete.feature 2. Instructor cannot delete student's response
        Using selenium
        Given there is a sample response
        Given I am test_instructor in Sample Course
        
        Given the home workspace is loaded
        When I select "Student One" as the owner in the Composition column
        Then the owner is "Student One" in the Composition column
        Then the composition panel has 1 response named "Sample Assignment Response"
        The "Sample Assignment Response" project has no delete icon
        
        Finished using Selenium

    Scenario: homepage.delete.feature 3. Instructor can delete his own assignment
        Using selenium
        Given there is a sample assignment
        Given I am test_instructor in Sample Course
        
        Given the home workspace is loaded
        The "Sample Assignment" project has a delete icon
        
        When I click the "Sample Assignment" project delete icon
        Then I cancel the action
        The "Sample Assignment" project has a delete icon
        Then there is a "Sample Assignment" link
        
        When I click the "Sample Assignment" project delete icon
        Then I confirm the action
        
        Then there is not a "Sample Assignment" link
        
        Finished using Selenium
        
    Scenario: homepage.delete.feature 4. Student can delete his own response
        Using selenium
        Given there is a sample response
        Given I am test_student_one in Sample Course
        
        Given the home workspace is loaded
        The "Sample Assignment Response" project has no delete icon
        
        # Add a title and some text
        When I click the "Sample Assignment Response" link
        Then I am at the Sample Assignment Response page
        
        # Save
        When I click the Saved button
        Then I set the project visibility to "Private - only author(s) can view"
        Then I save the changes
        Then there is a "Private" link

        When I click the "Sample Course" link
        Given the home workspace is loaded
        
        When I click the "Sample Assignment Response" project delete icon
        Then I cancel the action
        
        When I click the "Sample Assignment Response" project delete icon
        Then I confirm the action
        
        Then there is not a "Sample Assignment Response" link
        Then the composition panel has 1 project named "Sample Assignment"
        
        Finished using Selenium
   
