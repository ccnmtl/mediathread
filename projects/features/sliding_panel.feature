Feature: Sliding Panels
        
     Scenario Outline: 1. Composition At Various Resolutions
        Using selenium
        Given I am test_instructor in Sample Course
        Given my browser resolution is <width> x <height>
        
        # Composition Editing
        There is a Create Composition button
        When I click the Create Composition button
        Then I am at the Untitled page
        There is an open Composition panel
        And the Composition panel has an open subpanel
        
        # Composition has to be saved or 
        # other tests will get a save dialog
        Then I call the Composition "Sliding Panel: Scenario 1 <width> x <height>"
        When I click the Save button
        Then I see a Save Changes dialog
        Then I save the changes
        
        Finished using Selenium
        
      Examples:
        | width | height | 
        | 1024  | 768    |
        | 1280  | 800    |
        | 1440  | 900    |
        
    Scenario Outline: 2. Assignment At Various Resolutions
        Using selenium
        Given there is a sample assignment
        Given I am test_student_one in Sample Course
        Given my browser resolution is <width> x <height>
        
        # Assignment View
        There is an assignment "Sample Assignment" project by Instructor One
        When I click the "Sample Assignment" link
        Then I am at the Sample Assignment page
        
        There is an open Assignment panel
        And the Assignment panel has an open subpanel
        
        # Assignment Response
        When I click the Respond to Assignment button
        Then there is an open Assignment panel
        And the Assignment panel has a closed subpanel
        Then there is an open Composition panel
        And the Composition panel has a closed subpanel

        # Composition has to be saved or 
        # other tests will get a save dialog
        Then I call the Composition "Sliding Panel: Scenario 2 <width> x <height>"
        When I click the Save button
        Then I see a Save Changes dialog
        Then I save the changes
        
        # Delete the response from the home screen
        When I click the HOME button
        Then I wait 2 seconds
        Then I delete "Sliding Panel: Scenario 2 <width> x <height>"
        
        Finished using Selenium
        
      Examples:
        | width | height | 
        | 1024  | 768    |
        | 1280  | 800    |
        | 1440  | 900    |        
         