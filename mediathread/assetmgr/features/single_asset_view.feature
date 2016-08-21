Feature: Single Asset View

    Scenario: single_asset_view.feature 1. Basic Item View
        Using selenium
        Given there are sample assets
        Given I am instructor_one in Sample Course

        When I view the "MAAP Award Reception" asset
        Given the asset workspace is loaded

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

        # Verify the Quick Help popup is visible
        Contextual help is visible for the asset
        When I close the asset's contextual help
        Contextual help is not visible for the asset

        # Verify the Sources tab
        When I click the "Source" link
        And there is an "Item Permalink" link

        Finished using Selenium

    Scenario: single_asset_view.feature 2. Edit global annotation
        Using selenium
        Given there are sample assets
        Given I am instructor_one in Sample Course

        When I view the "MAAP Award Reception" asset
        Given the asset workspace is loaded
        I close the asset's contextual help

        # Verify the asset is really there
        The item header is "MAAP Award Reception"
        And the item notes are "instructor_one item note"
        And the item has the tag "instructor_one_item"
        And the item notes are not "Here are my notes"
        And the item does not have the tag "abc"
        When I edit the item
        Then there is a Cancel button
        And there is a Save Item button

        When I set the "Title" "text" field to "Updated MAAP Award Reception"
        And I remove the item tags
        And I set the item tags to "abc"
        And I set the "Notes" "textarea" field to "Here are my notes"
        And I click the Save Item button

        Then the item header is "Updated MAAP Award Reception"
        And the item notes are "Here are my notes"
        And the item has the tag "abc"
        And the item notes are not "instructor_one item note"
        And the item does not have the tag "flickr, instructor_one"

        Finished using Selenium

    Scenario: single_asset_view.feature 3. Edit global annotation as student
        Using selenium
        Given there are sample assets
        Given I am student_one in Sample Course

        When I view the "MAAP Award Reception" asset
        Given the asset workspace is loaded
        I close the asset's contextual help

        # Verify the asset is really there
        The item header is "MAAP Award Reception"
        And the item notes are "student_one item note"
        And the item has the tag "student_one_item"
        And the item notes are not "Here are my notes"
        And the item does not have the tag "abc"

        When I edit the item
        Then there is a Cancel button
        And there is a Save Item button
        And there is not a "Title" "text" field

        And I remove the item tags
        And I set the item tags to "abc"
        And I set the "Notes" "textarea" field to "Here are my notes"
        And I click the Save Item button

        Then the item header is "MAAP Award Reception"
        And the item notes are "Here are my notes"
        And the item has the tag "abc"
        And the item notes are not "student_one item note"
        And the item does not have the tag "student_one_item"

        Finished using Selenium


    Scenario: single_asset_view.feature 4. References tab
        Using selenium
        Given there are sample assets
        Given I am student_one in Sample Course

        # Create a project from the home page
        There is a Create button
        When I click the Create button
        When I click the Create Composition button

        Given the composition workspace is loaded

        # Add a title and some text and an asset
        I call the Composition "Single Asset View 4"
        And I insert "MAAP Award Reception" into the text

        # Save
        When I click the Save button
        Then I set the project visibility to "Whole Class - all class members can view"
        Then I save the changes
        And there is a "Published to Class" link

        # Navigate to the asset
        When I view the "MAAP Award Reception" asset
        Given the asset workspace is loaded
        I close the asset's contextual help

        # Check the references tab
        Then I click the "References" link
        And I see "Tags"
        And there is a "flickr (1)" link
        And there is an "instructor_one_item (1)" link
        And there is an "instructor_one_selection (1)" link
        And there is a "student_one_item (1)" link
        And there is a "student_one_selection (1)" link
        And there is a "student_two_item (1)" link
        And there is a "student_two_selection (1)" link
        And I see "Class References"
        And there is a "Single Asset View 4" link

        Finished using Selenium
