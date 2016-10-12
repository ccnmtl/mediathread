Feature: QuickEdit

    Scenario: quickedit.feature 1. Instructor edits the item metadata
        Using selenium
        Given there are sample assets
        Given I am instructor_one in Sample Course

        # Create a project from the home page
        I click the Create button
        I click the Create Composition button

        Given the composition workspace is loaded

        # Add a title and some text
        Then I call the Composition "Quick Edit Composition"
        # Save the project (otherwise an "Unsaved" alert pops up)
        When I click the Save button
        I save the project changes

        # Verify asset exists
        And there is a "Mediathread: Introduction" link
        I see "instructor_one item note"
        And there is not an "abc" link

        # Click the +/Create button next to the asset
        When I click edit item for "Mediathread: Introduction"

        # Verify the create form is visible
        Then the "Edit Item" form appears
        And I set the quickedit "Notes" "textarea" field to "Here are my notes"
        And I set the item tags field to "ghi"
        And I click the Save Item button

        Then the "Edit Item" form disappears
        And I see "Here are my notes"
        And there is an "ghi" link

        Finished using Selenium

    Scenario: quickedit.feature 2. Instructor creates a selection
        Using selenium
        Given there are sample assets
        Given I am instructor_one in Sample Course

        # Create a project from the home page
        I click the Create button
        I click the Create Composition button

        Given the composition workspace is loaded

        # Add a title and some text
        Then I call the Composition "Quick Edit Composition"
        # Save the project (otherwise an "Unsaved" alert pops up)
        When I click the Save button
        I save the project changes

        # Verify asset exists
        And there is a "Mediathread: Introduction" link

        # Click the +/Create button next to the asset
        When I click create selection for "Mediathread: Introduction"

        # Verify the create form is visible
        Then the "Create Selection" form appears
        And I see "Title"
        And I see "Tags"
        And I see "Notes"
        And there is a Cancel button
        And there is a Save Selection button

        When I set the quickedit "Title" "text" field to "Test Selection"
        And I set the selection tags field to "abc"
        And I set the quickedit "Selection Notes" "textarea" field to "Here are my new notes"
        And I click the Save Selection button

        Then the "Create Selection" form disappears
        And I scroll to the "Test Selection" link
        And I see "Here are my new notes"
        And there is an "abc" link

        Finished using Selenium

    Scenario: quickedit.feature 3. Instructor edits a selection
        Using selenium
        Given there are sample assets
        Given I am instructor_one in Sample Course

        # Create a project from the home page
        I click the Create button
        I click the Create Composition button

        Given the composition workspace is loaded

        # Add a title and some text
        Then I call the Composition "Quick Edit Composition"
        # Save the project (otherwise an "Unsaved" alert pops up)
        When I click the Save button
        I save the project changes

        # Verify asset exists
        And there is a "Mediathread: Introduction" link

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
        And I set the selection tags field to "def"
        And I set the quickedit "Selection Notes" "textarea" field to "Here are my selection notes"
        And I click the Save Selection button

        Then the "Edit Selection" form disappears
        Then there is a "Test Selection" link
        And I see "Here are my selection notes"
        And there is an "def" link

        Finished using Selenium

