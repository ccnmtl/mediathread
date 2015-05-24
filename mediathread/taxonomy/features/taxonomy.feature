Feature: Taxonomy

    Scenario: taxonomy.feature 1. Create Taxonomy
        Using selenium
        Given I am test_instructor in Sample Course
        
        When I open the manage menu
        Then there is a "Vocabulary" link
        When I click the "Vocabulary" link
        Then I am at the Course Vocabulary page
        
        Given the taxonomy workspace is loaded
        I see "Create Concept"
        
        # Create a taxonomy
        When I create a new concept
        I see "Type concept name here"

        # Name and save
        I name the concept "Colors"
        I create the concept

        Then there is a "Colors" link
        And I see "Create Concept"
        And I see "Colors Concept"
        And I see "Terms"
        And I see "Type new term name here"
        
    Scenario: taxonomy.feature 2. Duplicate Taxonomy
        Using selenium
        Given I am test_instructor in Sample Course
        
        # shortcut to taxonomy
        When I access the url "/taxonomy/"
        Given the taxonomy workspace is loaded
        I see "Create Concept"
        
        # Create a taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept
        Then there is a "Colors" link
        
        # Duplicate taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept
        
        I'm told "A Colors concept exists. Please choose another name"
        
    Scenario: taxonomy.feature 3. Delete Taxonomy
        Using selenium
        Given I am test_instructor in Sample Course
        
        # shortcut to taxonomy
        When I access the url "/taxonomy/"
        Given the taxonomy workspace is loaded
        I see "Create Concept"
        
        # Create a taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept
        Then there is a "Colors" link
        
        # Delete the taxonomy
        When I click the "Colors" link
        Then the "Colors" concept has a delete icon
        
        When I click the "Colors" concept delete icon
        And I confirm the action
        
        Then there is not a "Colors" link
        
    Scenario: taxonomy.feature 4. Edit Taxonomy
        Using selenium
        Given I am test_instructor in Sample Course
        
        # shortcut to taxonomy
        When I access the url "/taxonomy/"
        Given the taxonomy workspace is loaded
        I see "Create Concept"
        
        # Create a taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept
        Then there is a "Colors" link
        
        # Edit the taxonomy
        When I click the "Colors" link
        Then the "Colors" concept has an edit icon
        
        When I click the "Colors" concept edit icon        
        I see "Type concept name here"
        
        # Name and save
        I rename the "Colors" concept to "Shapes"
        I save the concept

        Then there is a "Shapes" link
        Then there is not a "Colors" link
        And I see "Create Concept"
        And I see "Shapes Concept"
        And I see "Terms"
        And I see "Type new term name here"

    Scenario: taxonomy.feature 5. Create Term
        Using selenium
        Given I am test_instructor in Sample Course
        
        # shortcut to taxonomy
        When I access the url "/taxonomy/"
        Given the taxonomy workspace is loaded
        I see "Create Concept"
        
        # Create a taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept
        Then there is a "Colors" link  
        
        # Create a term
        When I name a term "Red"
        And create the term
        Then I see a "Red" term
        
    Scenario: taxonomy.feature 6. Duplicate Term
        Using selenium
        Given I am test_instructor in Sample Course
        
        # shortcut to taxonomy
        When I access the url "/taxonomy/"
        Given the taxonomy workspace is loaded
        I see "Create Concept"
        
        # Create a taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept
        Then there is a "Colors" link  
        
        # Create a term
        When I name a term "Red"
        And create the term
        Then I see a "Red" term
        
        # Duplicate term
        When I name a term "Red"
        And create the term
        Then I'm told "Red term already exists. Please choose a new name"
        
    Scenario: taxonomy.feature 7. Delete Term
        Using selenium
        Given I am test_instructor in Sample Course
        
        # shortcut to taxonomy
        When I access the url "/taxonomy/"
        Given the taxonomy workspace is loaded
        I see "Create Concept"
        
        # Create a taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept
        Then there is a "Colors" link  
        
        # Create a term
        When I name a term "Red"
        And create the term
        Then I see a "Red" term
        
        # Delete the term
        When I click the "Red" term delete icon
        And I confirm the action
        Then there is no "Red" term
        
                 
    Scenario: taxonomy.feature 8. Edit Term
        Using selenium
        Given I am test_instructor in Sample Course
        
        # shortcut to taxonomy
        When I access the url "/taxonomy/"
        Given the taxonomy workspace is loaded
        I see "Create Concept"
        
        # Create a taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept
        Then there is a "Colors" link  
        
        # Create a term
        When I name a term "Red"
        And create the term
        Then I see a "Red" term

        # Edit the term
        When I click the "Red" term edit icon
        I rename the "Red" term to "Blue"
        I save the term

        Then I see a "Blue" term
        Then there is no "Red" term