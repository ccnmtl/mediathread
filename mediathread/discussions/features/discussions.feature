Feature: Discussion View

    Scenario: discussion.feature 1. Create a discussion
        Using selenium
        Given I am instructor_one in Sample Course

        There is a Create button
        When I click the Create button

        When I click the Create Discussion button
        Then I am at the Discussion page

        When I click the Save Comment button

        Then there is a Respond button
        And there is an Edit button

        When I click the "Sample Course" link
        Given the home workspace is loaded
        There is a "Discussion Title" link
        When I click the "Discussion Title" link
        Then I am at the Discussion page

        Finished using Selenium
