Feature: Single Asset View    
    
    Scenario: single_asset_view.feature 1. Basic Item View
        Using selenium
        Given I am test_instructor in Sample Course
        
        When I access the url "/asset/2/"
        Then there is a minimized Collection panel        
        And there is an open Asset panel
        
        # Verify the asset is really there
        The item header is "MAAP Award Reception"
        There is an "Item" link
        There is a "Source" link
        There is a "References" link        
        And there is not an Edit this item button
        And there is a View button
        And there is a Create button
                
        Finished using Selenium
        
    Scenario: single_asset_view.feature 2. Edit global annotation
        Using selenium
        Given I am test_instructor in Sample Course
        
        When I access the url "/asset/2/"
        Then there is a minimized Collection panel        
        And there is an open Asset panel
        And the asset workspace is loaded
        
        # Verify the asset is really there
        The item header is "MAAP Award Reception"
        And I see "instructor one item note"
        And I see "flickr, instructor_one"
        And I do not see "Here are my notes"
        And I do not see "abc"
        When I edit the item
        Then there is a Cancel button
        And there is a Save button
        
        When I set the "Title" "text" field to "Updated MAAP Award Reception"
        And I set the "Tags" "text" field to "abc"
        And I set the "Notes" "textarea" field to "Here are my notes"
        And I click the Save button
        
        Then the item header is "Updated MAAP Award Reception"
        And I see "Here are my notes"
        And I see "abc"
        And I do not see "instructor one item note"
        And I do not see "flickr, instructor_one"
                        
        Finished using Selenium
        
    Scenario: single_asset_view.feature 3. Edit global annotation as student
        Using selenium
        Given I am test_student_one in Sample Course
        
        When I access the url "/asset/2/"
        Then there is a minimized Collection panel        
        And there is an open Asset panel
        And the asset workspace is loaded
        
        # Verify the asset is really there
        The item header is "MAAP Award Reception"
        And I see "student one item note"
        And I see "student_one_item"
        And I do not see "Here are my notes"
        And I do not see "abc"
        
        When I edit the item
        Then there is a Cancel button
        And there is a Save button
        And there is not a "Title" "text" field
        
        And I set the "Tags" "text" field to "abc"
        And I set the "Notes" "textarea" field to "Here are my notes"
        And I click the Save button
        
        Then the item header is "MAAP Award Reception"
        And I see "Here are my notes"
        And I see "abc"
        And I do not see "student one item note" in the item tab
        Then I wait 1 second
        And I do not see "student_one_item"
                        
        Finished using Selenium