Feature: Collection View    
    
    Scenario: collection.feature 1. Collection - Basic item functionality
        Using selenium
        Given I am test_instructor in Sample Course
        
        When I click the "View Full Collection" link
        Then I am at the Collection page
        Given the collection workspace is loaded
        
        Then the owner is "All Class Members" in the Collection column
        When I select "Me" as the owner
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has no notes
        And the "MAAP Award Reception" item has no tags
        And the "MAAP Award Reception" item has 3 selections, 1 by me
        And the "MAAP Award Reception" item has a delete icon
        And the "MAAP Award Reception" item has an edit icon
        
        When I select "Student One" as the owner
        Then the owner is "Student One" in the Collection column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 3 selections, 1 by me
        And the "MAAP Award Reception" item has no delete icon
        And the "MAAP Award Reception" item has an edit icon
        
        When I click the "MAAP Award Reception" item edit icon
        Then I am at the Mediathread Collection page
                
        Finished using Selenium

    Scenario Outline: collection.feature 2. Collection - Viewing Items & Selections
        Using selenium
        
        Given I am test_instructor in Sample Course
        Given the selection visibility is set to "<selection_visibility>"
        
        Given I am <user_name> in Sample Course
        Given I am at the Home page
        
        When I click the "View Full Collection" link
        Then I am at the Collection page
        Given the collection workspace is loaded
        
        # Instructor One
        When I select "Instructor One" as the owner
        Then the owner is "<instructor_one_relationship>" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has <total_selections> selections, 1 by me
        
        And I can filter by "instructor_one" in the asset-workspace column
        And I can filter by "instructor_one_selection" in the asset-workspace column
        
        # Student One
        When I select "Student One" as the owner
        And I clear all tags
        Then the owner is "<student_one_relationship>" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has <total_selections> selections, 1 by me
        
        And I can filter by "student_one_selection" in the asset-workspace column
        And I can filter by "student_one_item" in the asset-workspace column
        
        # All Class Members
        When I select "All Class Members" as the owner
        And I clear all tags
        Then the owner is "All Class Members" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has <total_selections> selections, 1 by me
        
        Then the Collection panel has a "Mediathread: Introduction" item

        Then the Collection panel has a "The Armory - Home to CCNMTL'S CUMC ..." item
        
        And I can filter by "instructor_one" in the asset-workspace column
        And I can filter by "instructor_one_selection" in the asset-workspace column
        And I can filter by "student_one_selection" in the asset-workspace column
        And I can filter by "student_one_item" in the asset-workspace column
        And I can filter by "student_two_selection" in the asset-workspace column
        And I can filter by "student_two_item" in the asset-workspace column
        
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has <total_selections> selections, 1 by me        
        
        Finished using Selenium
        
      Examples:
        | user_name           |  instructor_one_relationship  |  student_one_relationship | selection_visibility | total_selections |
        | test_instructor     |  Me                           |  Student One              | Yes                  | 3                |
        | test_student_one    |  Instructor One               |  Me                       | Yes                  | 3                |
        | test_student_two    |  Instructor One               |  Student One              | Yes                  | 3                |
        | test_instructor     |  Me                           |  Student One              | No                   | 3                |        
        
   Scenario: collection.feature 3. Collection - Limited Selection Visibility 
        Using selenium
        Given I am test_instructor in Sample Course
        Given the selection visibility is set to "No"

        Given I am test_student_one in Sample Course

        When I click the "View Full Collection" link
        Then I am at the Collection page
        Given the collection workspace is loaded
                
        # Student One can see his own & the instructors annotations
        # But, should see nothing to do with Student Two
        
        # Instructor One
        When I select "Instructor One" as the owner
        Then the owner is "Instructor One" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has no notes
        And the "MAAP Award Reception" item has no tags
        And the "MAAP Award Reception" item has no selections
        And the "MAAP Award Reception" item has 2 selections, 1 by me
        
        And I can filter by "instructor_one" in the asset-workspace column
        And I can filter by "instructor_one_selection" in the asset-workspace column
        
        # Student One
        When I select "Student One" as the owner
        And I clear all tags
        Then the owner is "Me" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 2 selections, 1 by me
        
        And I can filter by "student_one_selection" in the asset-workspace column
        And the "MAAP Award Reception" item has 1 selections, 1 by me
        
        And I can filter by "student_one_item" in the asset-workspace column
        
        # Student Two
        When I select "Student Two" as the owner
        And I clear all tags
        Then the owner is "Student Two" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 2 selections, 1 by me
        And I cannot filter by "student_two_selection" in the asset-workspace column
        And I cannot filter by "student_two_item" in the asset-workspace column
        
        # All Class Members
        When I select "All Class Members" as the owner
        And I clear all tags        
        Then the owner is "All Class Members" in the asset-workspace column
        
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 2 selections, 1 by me
        
        Then the Collection panel has a "Mediathread: Introduction" item

        Then the Collection panel has a "The Armory - Home to CCNMTL'S CUMC ..." item
        And the "The Armory - Home to CCNMTL'S CUMC ..." item has no notes
        And the "The Armory - Home to CCNMTL'S CUMC ..." item has no tags
        And the "The Armory - Home to CCNMTL'S CUMC ..." item has no selections
        
        And I can filter by "instructor_one" in the asset-workspace column
        And I can filter by "instructor_one_selection" in the asset-workspace column
        And I can filter by "student_one_selection" in the asset-workspace column
        And I can filter by "student_one_item" in the asset-workspace column
        And I cannot filter by "student_two_selection" in the asset-workspace column
        And I cannot filter by "student_two_item" in the asset-workspace column
                
        Finished using Selenium
    
    Scenario: collection.feature 4. Collection - Filter by tag
        Using selenium
        Given I am test_instructor in Sample Course
        
        When I click the "View Full Collection" link
        Then I am at the Collection page
        Given the collection workspace is loaded
        
        Then the owner is "All Class Members" in the asset-workspace column
        When I select "Me" as the owner

        Then the Collection panel has a "MAAP Award Reception" item
        And the Collection panel has a "The Armory - Home to CCNMTL'S CUMC ..." item
        And the Collection panel has a "Mediathread: Introduction" item
        
        And I can filter by "flickr" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the Collection panel has a "The Armory - Home to CCNMTL'S CUMC ..." item
        And the Collection panel has no "Mediathread: Introduction" item
        
        When I clear all tags
        Then the Collection panel has a "MAAP Award Reception" item
        And the Collection panel has a "The Armory - Home to CCNMTL'S CUMC ..." item
        And the Collection panel has a "Mediathread: Introduction" item
        
        And I can filter by "video" in the asset-workspace column
        Then the Collection panel has no "MAAP Award Reception" item
        And the Collection panel has no "The Armory - Home to CCNMTL'S CUMC ..." item
        And the Collection panel has a "Mediathread: Introduction" item

        Finished using Selenium

        