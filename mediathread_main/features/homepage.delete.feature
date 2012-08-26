Feature: Homepage

    Scenario: 1. Homepage - Student cannot delete assignment
        Using selenium
        Given there is a sample assignment
        Given I am test_student_one in Sample Course
        
        The "Sample Assignment" project has no delete icon
        
        # Direct delete url
        When I access the url "/project/delete/1/"
        Then I see "forbidden"
        
        Finished using Selenium 
        
    Scenario: 2. Homepage -- Instructor cannot delete student's response
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

    Scenario: 3. Homepage - Instructor can delete his own assignment
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
        
    Scenario: 4. Homepage - Student can delete his own response
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
   
