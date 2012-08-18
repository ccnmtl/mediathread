Feature: Homepage

    Scenario: 1. Homepage - Instructor Homepage
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
        And there is help for the Collection column
        Finished using Selenium
        
    Scenario: 2. Homepage - Student Homepage
        Using selenium
        Given I am test_student_one in Sample Course
        Then there is not an Instructor Dashboard button
        And there is not a FROM YOUR INSTRUCTOR column
        And there is an ANALYSIS column
        And there is help for the ANALYSIS column
        And there is a Compositions column
        And there is a Collection column
        And there is help for the Compositions column
        And there is help for the Collection column
        Finished using Selenium
        
    Scenario Outline: 3. Homepage - Collection Box - Viewing Items & Selections
        Using selenium
        
        Given I am test_instructor in Sample Course
        Given the selection visibility is set to "<selection_visibility>"
        
        Given I am <user_name> in Sample Course
        Given I am at the Home page
        
        # Instructor One
        When I select "Instructor One" as the owner in the Analysis column
        Then the owner is "<instructor_one_relationship>" in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has no notes
        And the "MAAP Award Reception" item has no tags
        And the "MAAP Award Reception" item has no selections
        And the "MAAP Award Reception" item has <total_selections> selections, 1 by me
        
        And I can filter by "instructor_one" in the Analysis column
        And I can filter by "instructor_one_selection" in the Analysis column
        
        # Student One
        When I select "Student One" as the owner in the Analysis column
        Then the owner is "<student_one_relationship>" in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has no notes
        And the "MAAP Award Reception" item has no tags
        And the "MAAP Award Reception" item has no selections
        And the "MAAP Award Reception" item has <total_selections> selections, 1 by me
        
        And I can filter by "student_one_selection" in the Analysis column
        And I can filter by "student_one_item" in the Analysis column
        
        # All Class Members
        When I select "All Class Members" as the owner in the Analysis column
        Then the owner is "All Class Members" in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has no notes
        And the "MAAP Award Reception" item has no tags
        And the "MAAP Award Reception" item has no selections
        And the "MAAP Award Reception" item has <total_selections> selections, 1 by me
        
        Then the Collection panel has a "Mediathread: Introduction" item
        And the "Mediathread: Introduction" item has no notes
        And the "Mediathread: Introduction" item has no tags
        And the "Mediathread: Introduction" item has no selections

        Then the Collection panel has a "The Armory - Home to CCNMTL'S CUMC ..." item
        And the "The Armory - Home to CCNMTL'S CUMC ..." item has no notes
        And the "The Armory - Home to CCNMTL'S CUMC ..." item has no tags
        And the "The Armory - Home to CCNMTL'S CUMC ..." item has no selections
        
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
        
   Scenario: 4. Homepage - Collection Box - Limited Selection Visibility 
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
        And the "MAAP Award Reception" item has no notes
        And the "MAAP Award Reception" item has no tags
        And the "MAAP Award Reception" item has no selections
        And the "MAAP Award Reception" item has 2 selections, 1 by me
        
        And I can filter by "student_one_selection" in the Analysis column
        And I can filter by "student_one_item" in the Analysis column
        
        # Student Two
        When I select "Student Two" as the owner in the Analysis column
        Then the owner is "Student Two" in the Analysis column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has no notes
        And the "MAAP Award Reception" item has no tags
        And the "MAAP Award Reception" item has no selections
        And the "MAAP Award Reception" item has 2 selections, 1 by me
        And I cannot filter by "student_two_selection" in the Analysis column
        And I cannot filter by "student_two_item" in the Analysis column
        
        # All Class Members
        When I select "All Class Members" as the owner in the Analysis column
        Then the owner is "All Class Members" in the Analysis column
        
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has no notes
        And the "MAAP Award Reception" item has no tags
        And the "MAAP Award Reception" item has no selections
        And the "MAAP Award Reception" item has 2 selections, 1 by me
        
        Then the Collection panel has a "Mediathread: Introduction" item
        And the "Mediathread: Introduction" item has no notes
        And the "Mediathread: Introduction" item has no tags
        And the "Mediathread: Introduction" item has no selections

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
    
    
         