Feature: Homepage Delete Operations. Project, Item

    Scenario: homepage.delete.feature 1. Student cannot delete assignment
        Using selenium
        Given there is a sample assignment
        Given I am test_student_one in Sample Course
        
        The "Sample Assignment" project has no delete icon
        
        # Direct delete url
        When I access the url "/project/delete/1/"
        Then I see "forbidden"
        
        Finished using Selenium 
        
    Scenario: homepage.delete.feature 2. Instructor cannot delete student's response
        Using selenium
        Given there is a sample assignment and response
        Given I am test_instructor in Sample Course
        
        When I select "Student One" as the owner in the Analysis column
        Then the owner is "Student One" in the Analysis column
        Then the classwork panel has 1 projects named "Sample Assignment Response"
        The "Sample Assignment Response" project has no delete icon
        
        # Direct delete url
        When I access the url "/project/delete/2/"
        Then I see "forbidden"
        
        Finished using Selenium

    Scenario: homepage.delete.feature 3. Instructor can delete his own assignment
        Using selenium
        Given there is a sample assignment
        Given I am test_instructor in Sample Course
        
        The "Sample Assignment" project has a delete icon
        
        When I click the "Sample Assignment" project delete icon
        Then I cancel an alert dialog
        
        When I click the "Sample Assignment" project delete icon
        Then I ok an alert dialog
        
        Then there is not a "Sample Assignment" link
        
        Finished using Selenium
        
    Scenario: homepage.delete.feature 4. Student can delete his own response
        Using selenium
        Given there is a sample assignment and response
        Given I am test_student_one in Sample Course
        
        The "Sample Assignment Response" project has a delete icon
        
        When I click the "Sample Assignment Response" project delete icon
        Then I cancel an alert dialog
        
        When I click the "Sample Assignment Response" project delete icon
        Then I ok an alert dialog
        
        Then there is not a "Sample Assignment Response" link
        
        Finished using Selenium
        
    Scenario: homepage.delete.feature 5. Instructor can remove an item from his own collection
        Using selenium
        Given there is a sample assignment
        Given I am test_instructor in Sample Course
        
        Then the owner is "Me" in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has a delete icon
        
        When I click the "MAAP Award Reception" item delete icon
        Then I cancel an alert dialog
        
        When I click the "MAAP Award Reception" item delete icon
        Then I ok an alert dialog
        
        Then the Collection panel has no "MAAP Award Reception" item
        
        Finished using Selenium
   
