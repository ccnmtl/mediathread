Feature: Sliding Panels

    Scenario Outline: 1. Composition At Various Resolutions
        Using selenium
        Given I am instructor_one in Sample Course
        Given my browser resolution is <width> x <height>

        # Composition Editing
        I click the Create button
        I click the Create Composition button

        Given the composition workspace is loaded
        There is an open Composition panel
        And the Composition panel has a <subpanel_state> subpanel

        # Composition has to be saved or
        # other tests will get a save dialog
        Then I call the Composition "Sliding Panel: Scenario 1 <width> x <height>"
        Then I click the Save button
        Then I save the project changes

        Finished using Selenium

      Examples:
        | width | height | subpanel_state |
        | 800   | 500    | closed         |
        | 1024  | 768    | open           |
        | 1280  | 800    | open           |
        | 1440  | 900    | open           |

    Scenario Outline: 2. Assignment At Various Resolutions
        Using selenium
        Given there is a sample assignment
        Given I am student_one in Sample Course
        Given my browser resolution is <width> x <height>

        # Assignment View
        When I click the "Sample Assignment" link

        Given the composition workspace is loaded
        There is an open Assignment panel
        And the Assignment panel has an <assignment_subpanel_state> subpanel

        # Assignment Response
        When I click the Respond to Assignment button
        Given the composition workspace is loaded
        Then there is an <assignment_panel_state> Assignment panel
        Then there is an open Composition panel
        And the Composition panel has a <composition_subpanel_state> subpanel

        # Composition has to be saved or 
        # other tests will get a save dialog
        Then I call the Composition "Sliding Panel: Scenario 2 <width> x <height>"
        When I click the Save button
        Then I save the project changes

        # Delete the response from the home screen
        When I click the "Sample Course" link
        Given the home workspace is loaded
            Then I click the "Sliding Panel: Scenario 2 <width> x <height>" project delete icon
            Then I confirm the action
            Then there is not a "Sliding Panel: Scenario 2 <width> x <height>" link

        Finished using Selenium

      Examples:
        | width | height | assignment_subpanel_state | assignment_panel_state | composition_subpanel_state |
        | 800   | 500    | closed                    | closed                 | closed                     |
        | 1024  | 768    | open                      | open                   | closed                     |
        | 1280  | 800    | open                      | open                   | open                       |
        | 1440  | 900    | open                      | open                   | open                       |