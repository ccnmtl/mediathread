Feature: Login

    Scenario: login.feature 1. Test Invalid Login
        Using selenium
        Given I am not logged in
        When I access the url "/"
        Then I am at the Login page
        When I type "foo" for username
        When I type "foo" for password
        When I click the Log In button
        Then I am at the Login page
        Finished using Selenium
        
    Scenario: login.feature 2. Test Student Login
        Using selenium
        Given I am not logged in
        When I access the url "/"
        Then I am at the Login page
        When I type "test_student_one" for username
        When I type "test" for password
        When I click the Log In button
        Then I am at the Home page
        When I log out
        Then I am at the Login page
        Finished using Selenium      

    Scenario: login.feature 3. Test Instructor Login
        Using selenium
        Given I am not logged in
        When I access the url "/"
        Then I am at the Login page
        When I type "test_instructor" for username
        When I type "test" for password
        When I click the Log In button
        Then I am at the Home page
        When I log out
        Then I am at the Login page
        Finished using Selenium      
