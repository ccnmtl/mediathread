Feature: Composition

    Scenario: 1. Composition - create
        Using selenium
        Given I am test_instructor in Sample Course
        
        There is a New Composition button
        When I click the New Composition button
        Then I am at the Untitled page
        
        There is a Composition panel
        There is a Collections column
        There is an Add Selection panel
        The Composition panel has a Revisions button
        And the Composition panel has a Preview button
        And the Composition panel has a Save button
        And the Composition panel has a +/- Author button
        
        I call the Composition "CCNMTL Mission"
        I write some text for the Composition
        
        Finished using Selenium