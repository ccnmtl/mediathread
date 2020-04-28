Feature: Sources

    Scenario: manage_sources.feature 1. Add & Remove External Source, verify navigation from Add to My Collection
        Using selenium
        Given there are sample suggested collections
        Given I am instructor_one in Sample Course

        When I click the "Course Settings" link
        Then I am at the Course Settings page
        When I click the "Sources" link
        Then I am at the Sources page

        # Add the YouTube Source
        When I add YouTube to the class
        Then I see "YouTube has been enabled for your class"
        Then there is an Remove button

        # Under Add to My Collection
        Given I am student_one in Sample Course
        And I see 1 source

        # Verify YouTube navigation works
        There is a "YouTube" link

        Finished using Selenium

    Scenario: manage_sources.feature 2. Remove External Source, verify navigation from Add to My Collection
        Using selenium
        Given there are sample suggested collections
        Given I am instructor_one in Sample Course

        When I click the "Course Settings" link
        Then I am at the Course Settings page
        When I click the "Sources" link
        Then I am at the Sources page

        # Add the YouTube Source
        When I add YouTube to the class
        Then I see "YouTube has been enabled for your class"
        Then there is an Remove button

        # Under Add to My Collection
        When I access the course url "/"
        I see 1 source

        #Remove
        When I access the course url "/dashboard/settings/"
        Then I am at the Course Settings page
        When I click the "Sources" link
        Then I am at the Sources page

        When I click the Remove button
        Then I see "YouTube has been disabled for your class"

        # Under Add to My Collection
        When I access the course url "/"
        I see 0 source

        Finished using Selenium
