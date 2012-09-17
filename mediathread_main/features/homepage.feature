Feature: Homepage

    Scenario: homepage.feature 0. Test Wait
        Using selenium
        Given I am test_instructor in Sample Course
        Given the home workspace is loaded
        Then the Collection panel has a "MAAP Award Reception" item
        Finished using Selenium

    Scenario: homepage.feature 1. Instructor default view
        Using selenium
        Given I am test_instructor in Sample Course
        There is an Instructor Dashboard button
        And there is a FROM YOUR INSTRUCTOR column
        And there is an ANALYSIS column
        And there is help for the FROM YOUR INSTRUCTOR column
        And there is help for the ANALYSIS column
        And there is a Compositions column
        And there is a Collection column
        And there is help for the Compositions column
        Finished using Selenium
        
    Scenario: homepage.feature 2. Student view w/o assignment
        Using selenium
        Given I am test_student_one in Sample Course
        Then there is not an Instructor Dashboard button
        And there is not a FROM YOUR INSTRUCTOR column
        And there is an ANALYSIS column
        And there is help for the ANALYSIS column
        And there is a Compositions column
        And there is a Collection column
        And there is help for the Compositions column
        Finished using Selenium

    Scenario: homepage.feature 3. Student view w/assignment
        Using selenium
        Given there is a sample assignment
        Given I am test_student_one in Sample Course
        
        And there is a FROM YOUR INSTRUCTOR column
        And there is no help for the FROM YOUR INSTRUCTOR column
        Then there is an assignment "Sample Assignment" project by Instructor One
        Then the instructor panel has 1 projects named "Sample Assignment"
        
        And there is an ANALYSIS column
        And there is no help for the ANALYSIS column
        
        When I click the "Sample Assignment" link
        Then I am at the Sample Assignment page
        And there is an open Assignment panel
        And the Assignment title is "Sample Assignment"
        
        Finished using Selenium
        
    Scenario: homepage.feature 4. Student view w/assignment & response
        Using selenium
        Given there is a sample assignment and response
        Given I am test_student_one in Sample Course
        
        There is a FROM YOUR INSTRUCTOR column
        The instructor panel has 1 projects named "Sample Assignment"
        And there is a submitted to instructor "Sample Assignment Response" project by Student One
        And I see "Response for"
        And there is a "Sample Assignment" link
        
        When I click the "Sample Assignment Response" link
        Then I am at the Sample Assignment Response page
        And there is an open Composition panel
        And the Composition title is "Sample Assignment Response"  
        
        Finished using Selenium    
                
    Scenario: homepage.feature 5. Collection - Basic item functionality
        Using selenium
        Given I am test_instructor in Sample Course
        
        Then the owner is "Me" in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has no notes
        And the "MAAP Award Reception" item has no tags
        And the "MAAP Award Reception" item has no selections
        And the "MAAP Award Reception" item has 3 selections, 1 by me
        And the "MAAP Award Reception" item has a delete icon
        And the "MAAP Award Reception" item has an edit icon
        
        When I select "Student One" as the owner in the Analysis column
        Then the owner is "Student One" in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 3 selections, 1 by me
        And the "MAAP Award Reception" item has no delete icon
        And the "MAAP Award Reception" item has an edit icon
        
        When I click the "MAAP Award Reception" item edit icon
        Then I am at the Mediathread Collection page
        When I click the HOME button
        Then I wait 2 seconds
        Then I am at the Home page
        
        When I click the View All Items button
        Then I am at the Mediathread Collection page
        
        Finished using Selenium
        
    Scenario Outline: homepage.feature 6. Collection - Viewing Items & Selections
        Using selenium
        
        Given I am test_instructor in Sample Course
        Given the selection visibility is set to "<selection_visibility>"
        
        Given I am <user_name> in Sample Course
        Given I am at the Home page
        
        # Instructor One
        When I select "Instructor One" as the owner in the Analysis column
        Then the owner is "<instructor_one_relationship>" in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has <total_selections> selections, 1 by me
        
        And I can filter by "instructor_one" in the Analysis column
        And I can filter by "instructor_one_selection" in the Analysis column
        
        # Student One
        When I select "Student One" as the owner in the Analysis column
        Then the owner is "<student_one_relationship>" in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has <total_selections> selections, 1 by me
        
        And I can filter by "student_one_selection" in the Analysis column
        And I can filter by "student_one_item" in the Analysis column
        
        # All Class Members
        When I select "All Class Members" as the owner in the Analysis column
        Then the owner is "All Class Members" in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has <total_selections> selections, 1 by me
        
        Then the Collection panel has a "Mediathread: Introduction" item

        Then the Collection panel has a "The Armory - Home to CCNMTL'S CUMC ..." item
        
        And I can filter by "instructor_one" in the Analysis column
        And I can filter by "instructor_one_selection" in the Analysis column
        And I can filter by "student_one_selection" in the Analysis column
        And I can filter by "student_one_item" in the Analysis column
        And I can filter by "student_two_selection" in the Analysis column
        And I can filter by "student_two_item" in the Analysis column
        
        Finished using Selenium
        
      Examples:
        | user_name           |  instructor_one_relationship  |  student_one_relationship | selection_visibility | total_selections |
        | test_instructor     |  Me                           |  Student One              | Yes                  | 3                |
        | test_student_one    |  Instructor One               |  Me                       | Yes                  | 3                |
        | test_student_two    |  Instructor One               |  Student One              | Yes                  | 3                |
        | test_instructor     |  Me                           |  Student One              | No                   | 3                |        
        
   Scenario: 7. homepage.feature 7. Collection - Limited Selection Visibility 
        Using selenium
        Given I am test_instructor in Sample Course
        Given the selection visibility is set to "No"

        Given I am test_student_one in Sample Course
        Given I am at the Home page
        
        # Student One can see his own & the instructors annotations
        # But, should see nothing to do with Student Two
        
        # Instructor One
        When I select "Instructor One" as the owner in the Analysis column
        Then the owner is "Instructor One" in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has no notes
        And the "MAAP Award Reception" item has no tags
        And the "MAAP Award Reception" item has no selections
        And the "MAAP Award Reception" item has 2 selections, 1 by me
        
        And I can filter by "instructor_one" in the Analysis column
        And I can filter by "instructor_one_selection" in the Analysis column
        
        # Student One
        When I select "Student One" as the owner in the Analysis column
        Then the owner is "Me" in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 2 selections, 1 by me
        
        And I can filter by "student_one_selection" in the Analysis column
        And I can filter by "student_one_item" in the Analysis column
        
        # Student Two
        When I select "Student Two" as the owner in the Analysis column
        Then the owner is "Student Two" in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 2 selections, 1 by me
        And I cannot filter by "student_two_selection" in the Analysis column
        And I cannot filter by "student_two_item" in the Analysis column
        
        # All Class Members
        When I select "All Class Members" as the owner in the Analysis column
        Then the owner is "All Class Members" in the Analysis column
        
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 2 selections, 1 by me
        
        Then the Collection panel has a "Mediathread: Introduction" item

        Then the Collection panel has a "The Armory - Home to CCNMTL'S CUMC ..." item
        And the "The Armory - Home to CCNMTL'S CUMC ..." item has no notes
        And the "The Armory - Home to CCNMTL'S CUMC ..." item has no tags
        And the "The Armory - Home to CCNMTL'S CUMC ..." item has no selections
        
        And I can filter by "instructor_one" in the Analysis column
        And I can filter by "instructor_one_selection" in the Analysis column
        And I can filter by "student_one_selection" in the Analysis column
        And I can filter by "student_one_item" in the Analysis column
        And I cannot filter by "student_two_selection" in the Analysis column
        And I cannot filter by "student_two_item" in the Analysis column
                
        Finished using Selenium
    
    Scenario: homepage.feature 8. Collection - Filter by tag
        Using selenium
        Given I am test_instructor in Sample Course
        
        Then the owner is "Me" in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the Collection panel has a "The Armory - Home to CCNMTL'S CUMC ..." item
        And the Collection panel has a "Mediathread: Introduction" item
        
        When I filter by "flickr" in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the Collection panel has a "The Armory - Home to CCNMTL'S CUMC ..." item
        And the Collection panel has no "Mediathread: Introduction" item
        
        When I clear the filter in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the Collection panel has a "The Armory - Home to CCNMTL'S CUMC ..." item
        And the Collection panel has a "Mediathread: Introduction" item
        
        When I filter by "video" in the Analysis column
        Then the Collection panel has no "MAAP Award Reception" item
        And the Collection panel has no "The Armory - Home to CCNMTL'S CUMC ..." item
        And the Collection panel has a "Mediathread: Introduction" item

        Finished using Selenium
        
    Scenario Outline: homepage.feature 9. User Settings menu
        Using selenium
        Given I am <user_name> in Sample Course
        
        When I open the user settings menu
        Then there is a "Log Out" link
        There is not a "Switch Course" link
        There is not an "Admin" link
        
        When I click the "Log Out" link
        Then I am at the Login page 

        Finished using Selenium
        
    Examples:
        | user_name           |
        | test_instructor     |
        | test_student_one    |
        
        
        
        
         