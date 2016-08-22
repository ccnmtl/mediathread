Feature: Collection View

    Scenario: collection.feature 1. Collection - Default Item & Selection View As Instructor
        Using selenium
        Given there are sample assets
        Given I am instructor_one in Sample Course

        When I click the "View Full Collection" link
        Given the collection workspace is loaded

        Then the owner is "All Class Members" in the Collection column
        When I select "Me" as the owner
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 1 by me
        And the "MAAP Award Reception" item has no delete icon
        And the "MAAP Award Reception" item has no edit icon

        And I can filter by "instructor_one_item (3)" in the Collection column
        When I clear all tags
        And I can filter by "instructor_one_selection (3)" in the Collection column
        When I clear all tags
        And I can filter by "flickr (2)" in the Collection column
        Then the Collection panel has a "MAAP Award Reception" item
        And the Collection panel has a "The Armory" item
        And the Collection panel has no "Mediathread: Introduction" item

        When I clear all tags
        Then the Collection panel has a "MAAP Award Reception" item
        And the Collection panel has a "The Armory" item
        And the Collection panel has a "Mediathread: Introduction" item

        And I can filter by "video (1)" in the Collection column
        Then the Collection panel has no "MAAP Award Reception" item
        And the Collection panel has no "The Armory" item
        And the Collection panel has a "Mediathread: Introduction" item

        When I clear all tags
        When I select "Student One" as the owner
        Then the owner is "Student One" in the Collection column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 0 by me

        And I can filter by "student_one_selection (1)" in the Collection column
        When I clear all tags
        And I can filter by "student_one_item (1)" in the Collection column

        # All Class Members
        When I select "All Class Members" as the owner
        And I clear all tags
        Then the owner is "All Class Members" in the Collection column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 3 selections, 1 by me

        Then the Collection panel has a "Mediathread: Introduction" item
        Then the Collection panel has a "The Armory" item

        And I can filter by "instructor_one_item (3)" in the Collection column
        And the "MAAP Award Reception" item has no selections

        When I clear all tags
        I can filter by "instructor_one_selection (3)" in the Collection column
        And the "MAAP Award Reception" item has 1 selections, 1 by me

        When I clear all tags
        I can filter by "student_one_selection (1)" in the Collection column
        And the "MAAP Award Reception" item has 1 selections, 0 by me

        When I clear all tags
        I can filter by "student_one_item (1)" in the Collection column
        The "MAAP Award Reception" item has no selections

        When I clear all tags
        I can filter by "student_two_selection (1)" in the Collection column
        And the "MAAP Award Reception" item has 1 selections, 0 by me

        When I clear all tags
        I can filter by "student_two_item (1)" in the Collection column
        The "MAAP Award Reception" item has no selections

        When I click the "MAAP Award Reception" link
        Then I am at the Mediathread Collection page

        Finished using Selenium

    Scenario: collection.feature 2. Collection - Default Item & Selection View as student_one
        Using selenium
        Given there are sample assets
        # Instructor sets visibility
        Given I am instructor_one in Sample Course
        Given the selection visibility is set to "Yes"

        # View as student
        Given I am student_one in Sample Course
        When I click the "View Full Collection" link

        # Instructor One
        Given the collection workspace is loaded
        When I select "Instructor One" as the owner
        Then the owner is "Instructor One" in the Collection column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 0 by me

        And I can filter by "instructor_one_item (3)" in the Collection column
        When I clear all tags
        And I can filter by "instructor_one_selection (3)" in the Collection column

        # Student One
        When I clear all tags
        And I select "Student One" as the owner
        Then the owner is "Me" in the Collection column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 1 by me

        And I can filter by "student_one_selection (1)" in the Collection column
        When I clear all tags
        And I can filter by "student_one_item (1)" in the Collection column

        # Student Two
        When I clear all tags
        And I select "Student Two" as the owner
        Then the owner is "Student Two" in the Collection column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 0 by me

        And I can filter by "student_two_item (1)" in the Collection column
        When I clear all tags
        And I can filter by "student_two_selection (1)" in the Collection column
        When I clear all tags

        # All Class Members
        When I select "All Class Members" as the owner
        And I clear all tags
        Then the owner is "All Class Members" in the Collection column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 3 selections, 1 by me

        Then the Collection panel has a "Mediathread: Introduction" item
        Then the Collection panel has a "The Armory" item

        I can filter by "instructor_one_item (3)" in the Collection column

        When I clear all tags
        I can filter by "instructor_one_selection (3)" in the Collection column

        When I clear all tags
        I can filter by "student_one_selection (1)" in the Collection column

        When I clear all tags
        I can filter by "student_one_item (1)" in the Collection column

        When I clear all tags
        I can filter by "student_two_selection (1)" in the Collection column

        When I clear all tags
        I can filter by "student_two_item (1)" in the Collection column

        Finished using Selenium


    Scenario: collection.feature 3. Collection - Limited Selection Visibility
        Using selenium
        Given there are sample assets
        Given I am instructor_one in Sample Course
        Given the selection visibility is set to "No"

        When I click the "View Full Collection" link
        Then I am at the Collection page
        Given the collection workspace is loaded

        # Instructor One
        When I select "Instructor One" as the owner
        Then the owner is "Me" in the Collection column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 1 by me

        And I can filter by "instructor_one_item (3)" in the Collection column

        When I clear all tags
        I can filter by "instructor_one_selection (3)" in the Collection column

        # Student One
        When I clear all tags
        And I select "Student One" as the owner
        Then the owner is "Student One" in the Collection column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 0 by me

        And I can filter by "student_one_selection (1)" in the Collection column

        When I clear all tags
        I can filter by "student_one_item (1)" in the Collection column

        # All Class Members
        When I select "All Class Members" as the owner
        And I clear all tags
        Then the owner is "All Class Members" in the Collection column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 3 selections, 1 by me

        Then the Collection panel has a "Mediathread: Introduction" item
        Then the Collection panel has a "The Armory" item

        And I can filter by "instructor_one_item (3)" in the Collection column

        When I clear all tags
        I can filter by "instructor_one_selection (3)" in the Collection column

        When I clear all tags
        I can filter by "student_one_selection (1)" in the Collection column

        When I clear all tags
        I can filter by "student_one_item (1)" in the Collection column

        When I clear all tags
        I can filter by "student_two_selection (1)" in the Collection column

        When I clear all tags
        I can filter by "student_two_item (1)" in the Collection column

        Finished using Selenium

   Scenario: collection.feature 4. Collection - Limited Item & Selection Visibility 
        Using selenium
        Given there are sample assets
        Given I am instructor_one in Sample Course
        Given the item visibility is set to "Yes"
        Given the selection visibility is set to "No"

        Given I am student_one in Sample Course

        When I click the "View Full Collection" link

        Given the collection workspace is loaded

        # Student One can see his own & the instructors annotations
        # But, should see nothing to do with Student Two
        # Except the fact that the item is in his collection

        # Instructor One
        When I select "Instructor One" as the owner
        Then the owner is "Instructor One" in the Collection column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 0 by me

        And I can filter by "instructor_one_item (3)" in the Collection column
        And I can filter by "instructor_one_selection (3)" in the Collection column

        # Student One
        When I clear all tags
        When I select "Student One" as the owner
        Then the owner is "Me" in the Collection column
        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 1 selections, 1 by me

        And I can filter by "student_one_selection (1)" in the Collection column
        And the "MAAP Award Reception" item has 1 selections, 1 by me

        And I can filter by "student_one_item (1)" in the Collection column

        # Student Two
        When I clear all tags
        When I select "Student Two" as the owner
        Then the owner is "Student Two" in the Collection column
        Then the Collection panel has a "MAAP Award Reception" item
        And I can filter by "student_two_selection (0)" in the Collection column
        When I clear all tags
        I can filter by "student_two_item (1)" in the Collection column

        # All Class Members
        When I clear all tags        
        When I select "All Class Members" as the owner
        Then the owner is "All Class Members" in the Collection column

        Then the Collection panel has a "MAAP Award Reception" item
        And the "MAAP Award Reception" item has 2 selections, 1 by me
        Then the Collection panel has a "Mediathread: Introduction" item
        Then the Collection panel has a "The Armory" item

        And I can filter by "instructor_one_item (3)" in the Collection column
        When I clear all tags
        And I can filter by "instructor_one_selection (3)" in the Collection column
        When I clear all tags
        And I can filter by "student_one_selection (1)" in the Collection column
        When I clear all tags
        And I can filter by "student_one_item (1)" in the Collection column
        When I clear all tags
        And I can filter by "student_two_selection (0)" in the Collection column
        When I clear all tags
        And I can filter by "student_two_item (1)" in the Collection column

        Finished using Selenium

