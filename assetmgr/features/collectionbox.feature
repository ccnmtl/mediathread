Feature: Collections Box

    Scenario: 1. Pick an Owner
        Using selenium
        Given I am test_student_one in Sample Course
        Then I am at the Home Page 
        When I select "Student Two" as the owner in the Analysis column
        Then the owner is "Student Two" in the Analysis column