Feature: Public Compositions

    Scenario Outline: publishtoworld.composition.feature 1. Instructor creates public to world composition - verify visibility 
        Using selenium
        Given there are sample assets
        Given I am instructor_one in Sample Course
        Given publish to world is enabled
        
        # Create a project from the home page
        I click the Create button
        I click the Create Composition button        

        Given the composition workspace is loaded
            # Add a title and some text
            Then I call the Composition "<project_name>"
            And I write some text for the Composition

            # Insert an asset
            Then I insert "<item_name>" into the text
            
            # Save
            When I click the Save button
            Then I set the project visibility to "Whole World - a public url is provided"
            Then I save the project changes
            Then there is a "permalink" link
            And there is a "Published to World" link
        
            Then I remember the "permalink" link
            Then I log out
            Then I navigate to the "permalink" link
        
        # Public Composition elements
        Given the composition workspace is loaded
            There is an open Composition panel
            I see "Instructor One"
            And I see "<project_name>"
            And there is a "permalink" link
            
            The Composition panel does not have a Revisions button
            And the Composition panel does not have an Edit button
            And the Composition panel does not have a Preview button
            And the Composition panel does not have a Saved button
            And the Composition panel does not have a +/- Author button
            
            When I click the "<item_name>" citation in the Composition panel
            Then the Composition panel media window displays "<item_name>"
        
        Finished using Selenium

      Examples:
        | project_name                    | item_name             |
        | Composition Public: Scenario 1A | MAAP Award Reception  |
        | Composition Public: Scenario 1B | Left Corner           |
