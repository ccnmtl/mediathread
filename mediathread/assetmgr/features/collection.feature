Feature: Collection View    
    
    Scenario: collection.feature 1. Collection - Basic item functionality
        Using selenium
        Given I am test_instructor in Sample Course

        When I click the "View Full Collection" link
        Given the collection workspace is loaded

        Then the owner is "All Class Members" in the Collection column
        When I select "Me" as the owner
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has no notes
        And the "MAAP Award Reception" item has no tags
        And the "MAAP Award Reception" item has 1 selections, 1 by me
        And the "MAAP Award Reception" item has no delete icon
        And the "MAAP Award Reception" item has no edit icon
        
        When I select "Student One" as the owner
        Then the owner is "Student One" in the Collection column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 0 by me
        
        When I click the "MAAP Award Reception" link
        Then I am at the Mediathread Collection page
                
        Finished using Selenium

    Scenario: collection.feature 2. Collection - Viewing Items & Selections
        Using selenium
        Given I am test_instructor in Sample Course
        Given the item visibility is set to "Yes"
        Given the selection visibility is set to "Yes"
        
        When I click the "View Full Collection" link
        
        # Instructor One
        Given the collection workspace is loaded
        When I select "Instructor One" as the owner
        Then the owner is "Me" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 1 by me
        
        And I can filter by "instructor_one (1)" in the asset-workspace column
        And I can filter by "instructor_one_selection (1)" in the asset-workspace column
        
        # Student One
        When I clear all tags
        And I select "Student One" as the owner
        Then the owner is "Student One" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 0 by me
        
        And I can filter by "student_one_selection (1)" in the asset-workspace column
        And I can filter by "student_one_item (1)" in the asset-workspace column
        
        # All Class Members
        When I select "All Class Members" as the owner
        And I clear all tags
        Then the owner is "All Class Members" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 3 selections, 1 by me
        
        Then the Collection panel has a "Mediathread: Introduction" item
        Then the Collection panel has a "The Armory - Home to CCNMTL'S CUMC…" item
        Then the Collection panel has a "Project Portfolio" item
        
        And I can filter by "instructor_one (1)" in the asset-workspace column
        And I can filter by "instructor_one_selection (1)" in the asset-workspace column
        And I can filter by "student_one_selection (1)" in the asset-workspace column
        And I can filter by "student_one_item (1)" in the asset-workspace column
        And I can filter by "student_two_selection (1)" in the asset-workspace column
        And I can filter by "student_two_item (1)" in the asset-workspace column
        
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 3 selections, 1 by me        
        
        Finished using Selenium
        
    Scenario: collection.feature 3. Collection - Viewing Items & Selections
        Using selenium

        # Instructor sets visibility        
        Given I am test_instructor in Sample Course
        Given the selection visibility is set to "Yes"
        
        # View as student
        Given I am test_student_one in Sample Course
        When I click the "View Full Collection" link
        
        # Instructor One
        Given the collection workspace is loaded
        When I select "Instructor One" as the owner
        Then the owner is "Instructor One" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 0 by me
        
        And I can filter by "instructor_one (1)" in the asset-workspace column
        And I can filter by "instructor_one_selection (1)" in the asset-workspace column
        
        # Student One
        When I clear all tags
        And I select "Student One" as the owner
        Then the owner is "Me" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 1 by me
        
        And I can filter by "student_one_selection (1)" in the asset-workspace column
        And I can filter by "student_one_item (1)" in the asset-workspace column
        
        # All Class Members
        When I select "All Class Members" as the owner
        And I clear all tags
        Then the owner is "All Class Members" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 3 selections, 1 by me
        
        Then the Collection panel has a "Mediathread: Introduction" item
        Then the Collection panel has a "The Armory - Home to CCNMTL'S CUMC…" item
        Then the Collection panel has a "Project Portfolio" item
        
        And I can filter by "instructor_one (1)" in the asset-workspace column
        And I can filter by "instructor_one_selection (1)" in the asset-workspace column
        And I can filter by "student_one_selection (1)" in the asset-workspace column
        And I can filter by "student_one_item (1)" in the asset-workspace column
        And I can filter by "student_two_selection (1)" in the asset-workspace column
        And I can filter by "student_two_item (1)" in the asset-workspace column
        
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 3 selections, 1 by me        
        
        Finished using Selenium        
        
    Scenario: collection.feature 4. Collection - Viewing Items & Selections
        Using selenium
        
        Given I am test_instructor in Sample Course
        Given the selection visibility is set to "Yes"
        
        Given I am test_student_two in Sample Course
        
        When I click the "View Full Collection" link
        
        # Instructor One
        Given the collection workspace is loaded
        When I select "Instructor One" as the owner
        Then the owner is "Instructor One" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 0 by me
        
        And I can filter by "instructor_one (1)" in the asset-workspace column
        And I can filter by "instructor_one_selection (1)" in the asset-workspace column
        
        # Student One
        When I clear all tags
        And I select "Student One" as the owner
        Then the owner is "Student One" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 0 by me
        
        And I can filter by "student_one_selection (1)" in the asset-workspace column
        And I can filter by "student_one_item (1)" in the asset-workspace column
        
        # All Class Members
        When I select "All Class Members" as the owner
        And I clear all tags
        Then the owner is "All Class Members" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 3 selections, 1 by me
        
        Then the Collection panel has a "Mediathread: Introduction" item
        Then the Collection panel has a "The Armory - Home to CCNMTL'S CUMC…" item
        Then the Collection panel has a "Project Portfolio" item
        
        And I can filter by "instructor_one (1)" in the asset-workspace column
        And I can filter by "instructor_one_selection (1)" in the asset-workspace column
        And I can filter by "student_one_selection (1)" in the asset-workspace column
        And I can filter by "student_one_item (1)" in the asset-workspace column
        And I can filter by "student_two_selection (1)" in the asset-workspace column
        And I can filter by "student_two_item (1)" in the asset-workspace column
        
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 3 selections, 1 by me        
        
        Finished using Selenium        
        
    Scenario: collection.feature 5. Collection - Viewing Items & Selections
        Using selenium
        
        Given I am test_instructor in Sample Course
        Given the selection visibility is set to "No"
        
        When I click the "View Full Collection" link
        Then I am at the Collection page
        Given the collection workspace is loaded
        
        # Instructor One
        When I select "Instructor One" as the owner
        Then the owner is "Me" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 1 by me
        
        And I can filter by "instructor_one (1)" in the asset-workspace column
        And I can filter by "instructor_one_selection (1)" in the asset-workspace column
        
        # Student One
        When I clear all tags
        And I select "Student One" as the owner
        Then the owner is "Student One" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 0 by me
        
        And I can filter by "student_one_selection (1)" in the asset-workspace column
        And I can filter by "student_one_item (1)" in the asset-workspace column
        
        # All Class Members
        When I select "All Class Members" as the owner
        And I clear all tags
        Then the owner is "All Class Members" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 3 selections, 1 by me
        
        Then the Collection panel has a "Mediathread: Introduction" item
        Then the Collection panel has a "The Armory - Home to CCNMTL'S CUMC…" item
        Then the Collection panel has a "Project Portfolio" item
        
        And I can filter by "instructor_one (1)" in the asset-workspace column
        And I can filter by "instructor_one_selection (1)" in the asset-workspace column
        And I can filter by "student_one_selection (1)" in the asset-workspace column
        And I can filter by "student_one_item (1)" in the asset-workspace column
        And I can filter by "student_two_selection (1)" in the asset-workspace column
        And I can filter by "student_two_item (1)" in the asset-workspace column
        
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 3 selections, 1 by me        
        
        Finished using Selenium
        
   Scenario: collection.feature 6. Collection - Limited Selection Visibility 
        Using selenium
        Given I am test_instructor in Sample Course
        Given the selection visibility is set to "No"

        Given I am test_student_one in Sample Course

        When I click the "View Full Collection" link

        Given the collection workspace is loaded
                
        # Student One can see his own & the instructors annotations
        # But, should see nothing to do with Student Two
        # Except the fact that the item is in his collection
        
        # Instructor One
        When I select "Instructor One" as the owner
        Then the owner is "Instructor One" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has no notes
        And the "MAAP Award Reception" item has no tags
        And the "MAAP Award Reception" item has no selections
        And the "MAAP Award Reception" item has 1 selections, 0 by me
        
        And I can filter by "instructor_one (1)" in the asset-workspace column
        And I can filter by "instructor_one_selection (1)" in the asset-workspace column
        
        # Student One
        When I clear all tags
        When I select "Student One" as the owner
        Then the owner is "Me" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 1 by me
        
        And I can filter by "student_one_selection (1)" in the asset-workspace column
        And the "MAAP Award Reception" item has 1 selections, 1 by me
        
        And I can filter by "student_one_item (1)" in the asset-workspace column
        
        # Student Two
        When I clear all tags
        When I select "Student Two" as the owner
        Then the owner is "Student Two" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And I cannot filter by "student_two_selection" in the asset-workspace column
        And I can filter by "student_two_item (1)" in the asset-workspace column
        
        # All Class Members
        When I clear all tags        
        When I select "All Class Members" as the owner
        Then the owner is "All Class Members" in the asset-workspace column
        
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 2 selections, 1 by me
        
        Then the Collection panel has a "Mediathread: Introduction" item

        Then the Collection panel has a "The Armory - Home to CCNMTL'S CUMC…" item
        And the "The Armory - Home to CCNMTL'S CUMC…" item has no notes
        And the "The Armory - Home to CCNMTL'S CUMC…" item has no tags
        And the "The Armory - Home to CCNMTL'S CUMC…" item has no selections
        
        And I can filter by "instructor_one (1)" in the asset-workspace column
        And I can filter by "instructor_one_selection (1)" in the asset-workspace column
        And I can filter by "student_one_selection (1)" in the asset-workspace column
        And I can filter by "student_one_item (1)" in the asset-workspace column
        And I cannot filter by "student_two_selection (1)" in the asset-workspace column
        And I can filter by "student_two_item (1)" in the asset-workspace column
                
        Finished using Selenium
    
    Scenario: collection.feature 7. Collection - Filter by tag
        Using selenium
        Given I am test_instructor in Sample Course
        
        When I click the "View Full Collection" link
        Given the collection workspace is loaded
        
        Then the owner is "All Class Members" in the asset-workspace column
        When I select "Me" as the owner

        Then the Collection panel has a "MAAP Award Reception" item
        And the Collection panel has a "The Armory - Home to CCNMTL'S CUMC…" item
        And the Collection panel has a "Mediathread: Introduction" item
        
        And I can filter by "flickr (2)" in the asset-workspace column
        Then the Collection panel has a "MAAP Award Reception" item
        And the Collection panel has a "The Armory - Home to CCNMTL'S CUMC…" item
        And the Collection panel has no "Mediathread: Introduction" item
        
        When I clear all tags
        Then the Collection panel has a "MAAP Award Reception" item
        And the Collection panel has a "The Armory - Home to CCNMTL'S CUMC…" item
        And the Collection panel has a "Mediathread: Introduction" item
        
        And I can filter by "video (2)" in the asset-workspace column
        Then the Collection panel has no "MAAP Award Reception" item
        And the Collection panel has no "The Armory - Home to CCNMTL'S CUMC…" item
        And the Collection panel has a "Mediathread: Introduction" item

        Finished using Selenium
