Feature: Homepage

    Scenario: 1. Instructor Homepage
        Using selenium
        Given I am logged in as test_instructor
        Given I am in the Sample Course class
        When I access the url "/"
        Then I am at the Home page
        There is an Instructor Dashboard button
        There is a FROM YOUR INSTRUCTOR column
        There is an ANALYSIS column
        There is help for the FROM YOUR INSTRUCTOR column
        There is help for the ANALYSIS column
        There is a Compositions column
        There is a Collections column
        There is help for the Compositions column
        There is help for the Collections column
        Finished using Selenium
        
    Scenario: 2. Student Homepage
        Using selenium
        Given I am logged in as test_student_one
        Given I am in the Sample Course class
        When I access the url "/"
        Then I am at the Home page
        Then there is not an Instructor Dashboard button
        There is not a FROM YOUR INSTRUCTOR column
        There is an ANALYSIS column
        There is help for the ANALYSIS column
        There is a Compositions column
        There is a Collections column
        There is help for the Compositions column
        There is help for the Collections column
        Finished using Selenium    