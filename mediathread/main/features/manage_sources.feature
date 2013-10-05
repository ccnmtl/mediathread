Feature: Sources

    Scenario: manage_sources.feature 1. View Add to My Collection, Add Sources, Enable Upload 
        Using selenium
        Given I am test_instructor in Sample Course
        
        There is not an "Upload from Computer" feature
        And I see 0 sources
        
        When I open the manage menu
        Then there is a "Sources" link
        When I click the "Sources" link
        Then I am at the Sources page
        
        # Enable Video Upload
        When I click the Enable Video Upload button
        Then I'm told "Mediathread Video Upload has been enabled for your class"       
        Then I confirm the action
        And I see "Upload Permission Settings"
        
        # Under Add to My Collection        
        When I click the "Sample Course" link
        Given the home workspace is loaded
        Then there is an "Upload from Computer" feature
        
        # On the Full Collection page
        When I access the url "/asset/"
        Then I am at the Mediathread Collection page
        
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
        When I click the "Sample Course" link
        Given the home workspace is loaded
        Then there is an "Upload from Computer" feature
        
        # Student cannot see
        When I log out
        When I click the Guest Log In button
        When I type "test_student_one" for username
        When I type "test" for password
        When I click the Log In button
        Then I am at the Home page
        Given the home workspace is loaded
        Then there is not an "Upload from Computer" feature

        Finished using Selenium
        
    Scenario: manage_sources.feature 3. Video Upload - Administrators Only 
        Using selenium
        Given I am test_instructor in Sample Course
        Given video upload is enabled
        
        # Set for administrators
        When I open the manage menu
        Then there is a "Sources" link
        When I click the "Sources" link
        Then I am at the Sources page
        When I allow Administrators to upload videos
        Then I'm told "Your changes have been saved"
        Then I confirm the action
        
        # Instructor cannot see
        When I click the "Sample Course" link
        Given the home workspace is loaded
        Then there is not an "Upload from Computer" feature
        
        # Student cannot see
        When I log out
        When I click the Guest Log In button
        When I type "test_student_one" for username
        When I type "test" for password
        When I click the Log In button
        Then I am at the Home page
        Given the home workspace is loaded
        Then there is not an "Upload from Computer" feature
        
        Finished using Selenium
        
    Scenario: manage_sources.feature 4. Video Upload - Students Too 
        Using selenium
        Given I am test_instructor in Sample Course
        Given video upload is enabled
        
        # Set for students
        When I open the manage menu
        Then there is a "Sources" link
        When I click the "Sources" link
        Then I am at the Sources page
        When I allow Students to upload videos
        Then I'm told "Your changes have been saved"
        Then I confirm the action
        
        # Instructor can see
        When I click the "Sample Course" link
        Given the home workspace is loaded
        Then there is an "Upload from Computer" feature
        
        # Student can see
        When I log out
        When I click the Guest Log In button
        When I type "test_student_one" for username
        When I type "test" for password
        When I click the Log In button
        Then I am at the Home page
        Given the home workspace is loaded
        Then there is an "Upload from Computer" feature

        Finished using Selenium
        
    Scenario: manage_sources.feature 5. Video Upload - On Behalf Of Permissions
        Using selenium
        Given I am test_instructor in Sample Course
        Given video upload is enabled
        
        # Set for students
        When I open the manage menu
        Then there is a "Sources" link
        When I click the "Sources" link
        Then I am at the Sources page
        When I allow Students to upload videos
        Then I'm told "Your changes have been saved"
        Then I confirm the action
        
        # Regular Instructor cannot upload on behalf of
        When I click the "Sample Course" link
        Given the home workspace is loaded
        Then there is an "Upload from Computer" feature
        When I open the "Upload from Computer" feature
        Then I see "Upload video"
        And I see "Upload audio"        
        And I cannot upload on behalf of other users
        
        # Regular student cannot upload on someone's behalf
        Given I am test_student_one in Sample Course
        Given the home workspace is loaded
        Then there is an "Upload from Computer" feature
        When I open the "Upload from Computer" feature
        Then I see "Upload video"
        And I see "Upload audio"        
        And I cannot upload on behalf of other users
        
        # Student with special privileges can upload on someone's behalf
        Given I am test_ta in Sample Course
        Given the home workspace is loaded
        Then there is an "Upload from Computer" feature
        When I open the "Upload from Computer" feature
        Then I see "Upload video"
        And I see "Upload audio"        
        And I can upload on behalf of other users
        
        # Staff that are not a member of this class cannot upload on someone's behalf
        Given I am not logged in
        When I access the url "/"
        Then I am at the Login page
        When I click the Guest Log In button
        When I type "test_staff" for username
        When I type "test" for password
        When I click the Log In button        
        Then I am at the Switch Course page        
        When I click the "Sample Course" link
        Then I am in the Sample Course class
        
        Given the home workspace is loaded
        Then there is an "Upload from Computer" feature
        When I open the "Upload from Computer" feature
        Then I do not see "Upload video"
        And I do not see "Upload audio"        
        And there is not an Upload audio button        
        And I cannot upload on behalf of other users
        And I see "You must be a course member to upload media files."
        And I cannot upload on behalf of other users
        
    Scenario: manage_sources.feature 6. Add & Remove External Source, verify navigation from Add to My Collection
        Using selenium
        Given I am test_instructor in Sample Course
        
        When I open the manage menu
        Then there is a "Sources" link
        When I click the "Sources" link
        Then I am at the Sources page
        
        # Add the YouTube Source
        When I add YouTube to the class
        Then I'm told "You Tube has been enabled for your class"
        Then I confirm the action
        Then there is an Remove button

        # Under Add to My Collection
        Given I am test_student_one in Sample Course
        Given the home workspace is loaded
        And I see 1 source
        
        # Verify YouTube navigation works
        When I click the "You Tube" link
        Then I am at the YouTube page
        
    Scenario: manage_sources.feature 7. Remove External Source, verify navigation from Add to My Collection
        Using selenium
        Given I am test_instructor in Sample Course
        
        When I open the manage menu
        Then there is a "Sources" link
        When I click the "Sources" link
        Then I am at the Sources page
        
        # Add the YouTube Source
        When I add YouTube to the class
        Then I'm told "You Tube has been enabled for your class"
        Then I confirm the action
        Then there is an Remove button
        
        # Under Add to My Collection
        When I click the "Sample Course" link
        I see 1 source
        
        #Remove
        When I open the manage menu
        Then there is a "Sources" link
        When I click the "Sources" link
        Then I am at the Sources page
        
        When I click the Remove button
        Then I'm told "You Tube has been disabled for your class"
        Then I confirm the action

        # Under Add to My Collection
        When I click the "Sample Course" link
        I see 0 source
