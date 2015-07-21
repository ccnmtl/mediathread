Feature: QuickEdit

    Scenario: quickedit.feature 1. Instructor edits the item metadata
        Using selenium
        Given I am test_instructor in Sample Course
        Given there are no projects

        # Create a project from the home page
        Given the home workspace is loaded
        There is a Create button
        When I click the Create button
        Then there is a Create Composition button
        When I click the Create Composition button        

        Given the composition workspace is loaded
        Then I am at the Untitled page
        Then I see "by Instructor One"
        And I see "Private"

        # Add a title and some text
        Then I call the Composition "Quick Edit Composition"
        
        # Verify asset exists
        And there is a "MAAP Award Reception" link
        I see "instructor one item note"
        And there is not an "abc" link

        # Click the +/Create button next to the asset
        When I click edit item for "MAAP Award Reception"
        
        # Verify the create form is visible
        Then the "Edit Item" form appears
        And I set the quickedit "Tags" "text" field to "abc"
        And I set the quickedit "Notes" "textarea" field to "Here are my notes"
        And I click the Save Item button

        Then the "Edit Item" form disappears
        And I see "Here are my notes"
        And there is an "abc" link
        
        # Save the project (otherwise an "Unsaved" alert pops up)
        When I click the Save button
        I save the changes

        Finished using Selenium

    Scenario: quickedit.feature 2. Instructor creates a selection
        Using selenium
        Given I am test_instructor in Sample Course
        Given there are no projects

        # Create a project from the home page
        Given the home workspace is loaded
        There is a Create button
        When I click the Create button
        Then there is a Create Composition button
        When I click the Create Composition button        

        Given the composition workspace is loaded
        Then I am at the Untitled page
        Then I see "by Instructor One"
        And I see "Private"

        # Add a title and some text
        Then I call the Composition "Quick Edit Composition"
        
        # Verify asset exists
        And there is a "MAAP Award Reception" link
        
        # Click the +/Create button next to the asset
        When I click create selection for "MAAP Award Reception"
        
        # Verify the create form is visible
        Then the "Create Selection" form appears

        And I see "Title"
        And I see "Tags"
        And I see "Notes"
        And there is a Cancel button
        And there is a Save Selection button
        
        When I set the quickedit "Title" "text" field to "Test Selection"
        And I set the quickedit "Selection Tags" "text" field to "abc"
        And I set the quickedit "Selection Notes" "textarea" field to "Here are my notes"
        And I click the Save Selection button
        
        Then there is a "Test Selection" link
        And there is an "abc" link
        And I see "Here are my notes"
        
        # Save the project (otherwise an "Unsaved" alert pops up)
        When I click the Save button
        I save the changes
        
        Finished using Selenium
        
    Scenario: quickedit.feature 3. Instructor edits a selection
        Using selenium
        Given I am test_instructor in Sample Course
        Given there are no projects

        # Create a project from the home page
        Given the home workspace is loaded
        There is a Create button
        When I click the Create button
        Then there is a Create Composition button
        When I click the Create Composition button        

        Given the composition workspace is loaded
        Then I am at the Untitled page
        Then I see "by Instructor One"
        And I see "Private"

        # Add a title and some text
        Then I call the Composition "Quick Edit Composition"
        
        # Verify asset exists
        And there is a "MAAP Award Reception" link
        
        # Click the +/Create button next to the asset
        When I click edit selection for "Manage Sources"
        
        # Verify the create form is visible
        Then the "Edit Selection" form appears

        And I see "Title"
        And I see "Tags"
        And I see "Notes"
        And there is a Cancel button
        And there is a Save Selection button
        
        When I set the quickedit "Title" "text" field to "Test Selection"
        And I set the quickedit "Selection Tags" "text" field to "abc"
        And I set the quickedit "Selection Notes" "textarea" field to "Here are my notes"
        And I click the Save Selection button
        
        Then there is a "Test Selection" link
        And there is an "abc" link
        And I see "Here are my notes"
        
        # Save the project (otherwise an "Unsaved" alert pops up)
        When I click the Save button
        I save the changes
        
        Finished using Selenium        

        
        

        


