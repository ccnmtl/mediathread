Feature: Homepage

    Scenario: 1. Homepage - Instructor Homepage
        Using selenium
        Given I am test_instructor in Sample Course
        There is an Instructor Dashboard button
        And there is a FROM YOUR INSTRUCTOR column
        And there is an ANALYSIS column
        And there is help for the FROM YOUR INSTRUCTOR column
        And there is help for the ANALYSIS column
        And there is a Compositions column
        And there is a Collections column
        And there is help for the Compositions column
        And there is help for the Collections column
        Finished using Selenium
        
    Scenario: 2. Homepage - Student Homepage
        Using selenium
        Given I am test_student_one in Sample Course
        Then there is not an Instructor Dashboard button
        And there is not a FROM YOUR INSTRUCTOR column
        And there is an ANALYSIS column
        And there is help for the ANALYSIS column
        And there is a Compositions column
        And there is a Collections column
        And there is help for the Compositions column
        And there is help for the Collections column
        Finished using Selenium    