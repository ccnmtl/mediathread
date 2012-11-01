Feature: Manage Sources

    Scenario: manage_sources.feature 1. View Add to My Collection, Add Sources, Enable Upload 
        Using selenium
        Given I am test_instructor in Sample Course
        
        When I click the Add to My Collection button
        Then I am at the Add to My Collection page
        And there is an Add to My Collection column
        And there is help for the Add to My Collection column
        And I do not see "Upload Video"
        And I see 0 sources
        
        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page
        
        When I click the Manage Sources button
        Then I am at the Manage Sources page
        
        # Enable Video Upload
        When I click the Enable Video Upload button
        Then I'm told "Mediathread Video Upload has been enabled for your class"
        And I see "Upload Permission Settings"
        
        # Under Add to My Collection        
        When I click the Add to My Collection button
        Then I am at the Add to My Collection page
        And I see "Upload Video"
        
        # On the Home Page
        When I click the HOME button
        Then I am at the Home page
        
        Given the home workspace is loaded
            The Collection panel has no "You Tube" item
            And the Collection panel has a "MAAP Award Reception" item
            And the Collection panel has a "Mediathread: Introduction" item
            And the Collection panel has a "The Armory - Home to CCNMTL'S CUMC ..." item
            
        Finished using Selenium
   
           
    Scenario: manage_sources.feature 2. Video Upload - Instructors Only
        Using selenium
        Given I am test_instructor in Sample Course
        Given video upload is enabled
        
        # By default, instructors and administrators are allowed to upload
        When I click the Add to My Collection button
        Then I see "Upload Video"
        
        # Student cannot see
        When I log out
        When I type "test_student_one" for username
        When I type "test" for password
        When I click the Log In button
        Then I am at the Home page
        When I click the Add to My Collection button
        Then I do not see "Upload Video"

        Finished using Selenium
        
    Scenario: manage_sources.feature 3. Video Upload - Administrators Only 
        Using selenium
        Given I am test_instructor in Sample Course
        Given video upload is enabled
        
        # Set for administrators
        When I click the Instructor Dashboard button
        Then I click the Manage Sources button
        Then I am at the Manage Sources page
        When I allow Administrators to upload videos
        Then I'm told "Your changes have been saved"
        
        # Instructor cannot see
        When I click the Add to My Collection button
        Then I do not see "Upload Video"
        
        # Student cannot see
        When I log out
        When I type "test_student_one" for username
        When I type "test" for password
        When I click the Log In button
        Then I am at the Home page
        When I click the Add to My Collection button
        Then I do not see "Upload Video"
        
        Finished using Selenium
        
    Scenario: manage_sources.feature 4. Video Upload - Students Too 
        Using selenium
        Given I am test_instructor in Sample Course
        Given video upload is enabled
        
        # Set for students
        When I click the Instructor Dashboard button
        When I click the Manage Sources button
        Then I am at the Manage Sources page
        When I allow Students to upload videos
        Then I'm told "Your changes have been saved"
        
        # Instructor can see
        When I click the Add to My Collection button
        Then I see "Upload Video"
        
        # Student can see
        When I log out
        When I type "test_student_one" for username
        When I type "test" for password
        When I click the Log In button
        Then I am at the Home page
        When I click the Add to My Collection button
        Then I see "Upload Video"

        Finished using Selenium
        
    Scenario: manage_sources.feature 5. Video Upload - On Behalf Of Permissions
        Using selenium
        Given I am test_instructor in Sample Course
        Given video upload is enabled
        
        # Set for students
        When I click the Instructor Dashboard button
        When I click the Manage Sources button
        Then I am at the Manage Sources page
        When I allow Students to upload videos
        Then I'm told "Your changes have been saved"
        
        # Regular Instructor cannot upload on behalf of
        When I click the Add to My Collection button
        Then I am at the Add to My Collection page
        Then I see "Upload Video"
        And I cannot upload on behalf of other users
        
        # Regular student cannot upload on someone's behalf
        Given I am test_student_one in Sample Course
        When I click the Add to My Collection button
        Then I am at the Add to My Collection page        
        Then I see "Upload Video"
        And I cannot upload on behalf of other users
        
        # Student with special privileges can upload on someone's behalf
        Given I am test_ta in Sample Course
        When I click the Add to My Collection button
        Then I am at the Add to My Collection page        
        Then I see "Upload Video"
        And I can upload on behalf of other users
        
        # Staff that are not a member of this class cannot upload on someone's behalf
        Given I am not logged in
        When I access the url "/"
        Then I am at the Login page
        When I type "test_staff" for username
        When I type "test" for password
        When I click the Log In button        
        Then I am at the Switch Course page        
        When I click the "Sample Course" link
        Then I am in the Sample Course class        
        When I click the Add to My Collection button
        Then I am at the Add to My Collection page        
        Then I see "Upload Video"
        And I see "You must be a course member to upload media files."
        And I cannot upload on behalf of other users
        
    Scenario: manage_sources.feature 6. Add External Source, verify navigation from Add to My Collection
        Using selenium
        Given I am test_instructor in Sample Course
        
        When I click the Instructor Dashboard button
        Then I am at the Instructor Dashboard page
        
        When I click the Manage Sources button
        Then I am at the Manage Sources page
        
        # Add the YouTube Source
        When I add YouTube to the class
        Then I'm told "You Tube has been enabled for your class"
        Then there is an Added button

        # Under Add to My Collection
        Given I am test_student_one in Sample Course        
        When I click the Add to My Collection button
        Then I am at the Add to My Collection page
        And I see 1 source
        
        # Verify YouTube navigation works
        When I click the "You Tube" link
        Then I am at the YouTube page
        
        Finished using Selenium