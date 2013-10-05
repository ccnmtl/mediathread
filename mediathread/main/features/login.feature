Feature: Login

    Scenario: login.feature 1. Test Invalid Login
        Using selenium
        Given I am not logged in
        When I access the url "/"
        Then I am at the Login page
        When I click the Guest Log In button
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
        When I click the Guest Log In button
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
        When I click the Guest Log In button
        When I type "test_instructor" for username
        When I type "test" for password
        When I click the Log In button
        Then I am at the Home page
        When I log out
        Then I am at the Login page
        Finished using Selenium
        
    Scenario: login.feature 4. Test Switch Course feature
        Using selenium
        Given I am not logged in
        When I access the url "/"
        Then I am at the Login page
        When I click the Guest Log In button
        When I type "test_student_three" for username
        When I type "test" for password
        When I click the Log In button
        
        Then I am at the Switch Course page
        Then there is an "Alternate Course" link
        Then there is an "Sample Course" link
        
        When I click the "Alternate Course" link
        Then I am in the Alternate Course class
        
        When I open the user menu
        Then there is a "Switch Course" link
        When I click the "Switch Course" link
        Then I am at the Switch Course page
        
        When I click the "Sample Course" link
        Then I am in the Sample Course class
        
        Finished using Selenium        