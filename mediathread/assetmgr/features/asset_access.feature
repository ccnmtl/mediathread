Feature: Direct Asset Access
    Verify that students and instructors cannot see each other's assets

    Scenario Outline: asset_access.feature 1. Sample Course members cannot see Alternate Course assets 
        Using selenium
        Given I am <user_name> in Sample Course

        # Direct Asset access view + json
        When I access the url "/asset/1/"
        Then I am at the Mediathread Collection page
        Then I see "Mediathread: Introduction"
        
        When I access the url "/asset/json/1/"
        Then I see "Page not found"
        
        When I access the url "/asset/2/"
        Then I am at the Mediathread Collection page
        Then I see "MAAP Award Reception"
        
        When I access the url "/asset/json/2/"
        Then I see "Page not found"
        
        When I access the url "/asset/3/"
        Then I am at the Mediathread Collection page
        Then I see "The Armory - Home to CCNMTL'S CUMC Office"
        
        When I access the url "/asset/json/3/"
        Then I see "Page not found"
        
        # Direct annotation access
        When I access the url "/asset/1/annotations/2/"
        Then I am at the Mediathread Collection page
        Then I see "Mediathread: Introduction"
        
        When I access the url "/asset/1/annotations/3/"
        Then I am at the Mediathread Collection page
        Then I see "Mediathread: Introduction"
        
        
        # Asset from the Alternate Course
        When I access the url "/asset/4/"
        Then I see "Page not found"
        When I access the url "/asset/json/4/"
        Then I see "Page not found"
        
        # Annotation from the Alternate Course
        When I access the url "/asset/4/annotations/13/"
        Then I see "Page not found"
    
        Finished using Selenium
        
    Examples:
        | user_name           |
        | test_instructor     |
        | test_student_one    |
        
    Scenario Outline: asset_access.feature 2. Alternate Course members cannot see Sample Course assets 
        Using selenium
        Given I am <user_name> in Alternate Course
        
        # Asset from the Alternate Course
        When I access the url "/asset/4/"
        Then I am at the Mediathread Collection page
        Then I see "Design Research"
        When I access the url "/asset/json/4/"
        Then I see "Page not found"
        
        # Annotation from the Alternate Course
        When I access the url "/asset/4/annotations/13/"
        Then I am at the Mediathread Collection page
        Then I see "Design Research"

        # Direct Asset access view + json
        When I access the url "/asset/1/"
        Then I see "Page not found"
        
        When I access the url "/asset/json/1/"
        Then I see "Page not found"
        
        When I access the url "/asset/2/"
        Then I see "Page not found"
        
        When I access the url "/asset/json/2/"
        Then I see "Page not found"
        
        When I access the url "/asset/3/"
        Then I see "Page not found"
        
        When I access the url "/asset/json/3/"
        Then I see "Page not found"
        
        # Direct annotation access
        When I access the url "/asset/1/annotations/2/"
        Then I see "Page not found"
        
        When I access the url "/asset/1/annotations/3/"
        Then I see "Page not found"
    
        Finished using Selenium
        
    Examples:
        | user_name           |
        | test_instructor_alt |
        | test_student_alt    |
        
    Scenario: asset_access.feature 3. Members of both classes can see all assets 
        Using selenium
        
        Given I am not logged in
        When I access the url "/"
        Then I am at the Login page
        When I click the Guest Log In button
        When I type "test_student_three" for username
        When I type "test" for password
        When I click the Log In button
        
        Then I am at the Switch Course page
        When I click the "Sample Course" link
        Then I am in the Sample Course class
        
        # Direct Asset access view + json
        When I access the url "/asset/json/1/"
        Then I see "Page not found"
        
        When I access the url "/asset/1/"
        Then I am at the Mediathread Collection page
        Then I see "Mediathread: Introduction"
        
        When I open the user menu
        Then there is a "Switch Course" link
        When I click the "Switch Course" link
        Then I am at the Switch Course page
        
        When I click the "Alternate Course" link
        Then I am in the Alternate Course class
        
        When I access the url "/asset/4/"
        Then I am at the Mediathread Collection page
        Then I see "Design Research"
        When I access the url "/asset/json/4/"
        Then I see "Page not found"
        
        Finished using Selenium
        
    Scenario: asset_access.feature 4. If logged into the wrong class, user is prompted to switch classes 
        Using selenium 
        
        Given I am not logged in
        When I access the url "/"
        Then I am at the Login page
        When I click the Guest Log In button
        When I type "test_student_three" for username
        When I type "test" for password
        When I click the Log In button
        
        Then I am at the Switch Course page
        When I click the "Sample Course" link
        Then I am in the Sample Course class
        
        # Try to access an asset from the Alternate Course
        When I access the url "/asset/4/"
        Then I see "Oops!"
        Then there is a "Go to Alternate Course" link
        Then there is a "Continue working in Sample Course" link
        
        When I click the "Continue working in Sample Course" link
        Then I am at the Home page
        
        When I access the url "/asset/4/"
        Then I see "Oops!"
        Then there is a "Go to Alternate Course" link
        Then there is a "Continue working in Sample Course" link
        
        When I click the "Go to Alternate Course" link
        Then I am in the Alternate Course class
        Then I am at the Mediathread Collection page
        Then I see "Design Research"
        
        Finished using Selenium