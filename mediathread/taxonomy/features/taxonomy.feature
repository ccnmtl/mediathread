Feature: Taxonomy

    Scenario: taxonomy.feature 1. Create, Duplicate, Delete Taxonomy
        Using selenium
        Given I am instructor_one in Sample Course

        When I click the "Course Settings" link
        Then I am at the Course Settings page
        When I click the "Vocabulary" link
        Then I am at the Vocabulary page

        Given the taxonomy workspace is loaded
        I see "Create Concept"

        # Create a taxonomy
        When I create a new concept
        I see "Concept name"

        # Name and save
        I name the concept "Colors"
        I create the concept

        Then there is a "Colors" concept
        And I see "Create Concept"
        And I see "Colors Concept"
        And I see "Terms"
        And I see "Type new term name here"
        
        # Duplicate taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept

        I'm told "A Colors concept exists. Please choose another name"

        # Delete the taxonomy
        When I click the "Colors" concept
        Then the "Colors" concept has a delete icon

        When I click the "Colors" concept delete icon
        And I confirm the action

        Then there is not a "Colors" concept

        Finished using Selenium

    Scenario: taxonomy.feature 2. Edit Taxonomy
        Using selenium
        Given I am instructor_one in Sample Course

        # shortcut to taxonomy
        When I access the url "/taxonomy/"
        Given the taxonomy workspace is loaded
        I see "Create Concept"

        # Create a taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept
        Then there is a "Colors" concept

        # Edit the taxonomy
        When I click the "Colors" concept
        Then the "Colors" concept has an edit icon

        When I click the "Colors" concept edit icon
        I see "Concept name"

        # Name and save
        I rename the "Colors" concept to "Shapes"
        I save the concept

        Then there is a "Shapes" concept
        Then there is not a "Colors" concept

        Finished using Selenium

    Scenario: taxonomy.feature 3. Create, Duplicate, Delete Term
        Using selenium
        Given I am instructor_one in Sample Course

        # shortcut to taxonomy
        When I access the url "/taxonomy/"
        Given the taxonomy workspace is loaded
        I see "Create Concept"

        # Create a taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept
        Then there is a "Colors" concept

        # Create a term
        When I name a term "Red"
        And create the term
        Then there is a "Red" term

        # Duplicate term
        When I name a term "Red"
        And create the term
        Then I'm told "Red term already exists. Please choose a new name"

        # Delete the term
        When I click the "Red" term delete icon
        And I confirm the action
        Then there is no "Red" term

        Finished using Selenium


    Scenario: taxonomy.feature 4. Edit Term
        Using selenium
        Given I am instructor_one in Sample Course

        # shortcut to taxonomy
        When I access the url "/taxonomy/"
        Given the taxonomy workspace is loaded
        I see "Create Concept"

        # Create a taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept
        Then there is a "Colors" concept

        # Create a term
        When I name a term "Red"
        And create the term
        Then there is a "Red" term

        # Edit the term
        When I click the "Red" term edit icon
        I rename the "Red" term to "Blue"
        I save the term
        I wait until the "Red" rename is complete

        Then there is a "Blue" term
        Then there is no "Red" term

        Finished using Selenium

    Scenario: taxonomy.feature 5. Create Term, Edit Taxonomy
        Using selenium
        Given I am instructor_one in Sample Course
        
        # shortcut to taxonomy
        When I access the url "/taxonomy/"
        Given the taxonomy workspace is loaded
        I see "Create Concept"
        
        # Create a taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept
        Then there is a "Colors" concept  
        
        # Create a term
        When I name a term "Red"
        And create the term
        Then there is a "Red" term
        
        # Edit the taxonomy
        When I click the "Colors" concept
        Then the "Colors" concept has an edit icon
        
        When I click the "Colors" concept edit icon        
        I see "Concept name"
        
        # Name and save
        I rename the "Colors" concept to "Shapes"
        I save the concept

        Then there is a "Shapes" concept
        Then there is not a "Colors" concept
    
        Finished using Selenium
        
    Scenario: taxonomy.feature 6. Create & Refresh from onomy
        Using selenium
        Given I am instructor_one in Sample Course

        # shortcut to taxonomy
        When I access the url "/taxonomy/"
        Given the taxonomy workspace is loaded
        I see "Create Concept"

        # Create a taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept
        Then there is a "Colors" concept

        When I click the Import button
        And specify the onomy url
        And confirm the onomy import

        Then there is a "Black" term
        Then there is a "Blue" term
        Then there is a "Green" term
        Then there is a "Pastels" term
        Then there is a "Purple" term
        Then there is a "Red" term

        Then there is a "Pastels" concept
        When I click the "Pastels" concept
        Then there is a "Light Blue" term
        Then there is a "Light Green" term
        Then there is a "Pink" term

        Then I click the "Colors" concept
        Then there is a "Red" term
        When I click the "Red" term delete icon
        And I confirm the action
        Then there is no "Red" term

        # refresh from the onomy url
        Then I click the Refresh button
        Then there is a "Red" term

        Finished using Selenium

    Scenario: taxonomy.feature 7. Try invalid Onomy url
        Using selenium
        Given I am instructor_one in Sample Course

        # shortcut to taxonomy
        When I access the url "/taxonomy/"
        Given the taxonomy workspace is loaded
        I see "Create Concept"

        # Create a taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept
        Then there is a "Colors" concept

        When I click the Import button
        And specify the incorrect onomy url
        And confirm the onomy import

        Then there is no "Black" term
        Then there is no "Blue" term
        Then there is no "Green" term
        Then there is no "Pastels" term
        Then there is no "Purple" term
        Then there is no "Red" term

        Finished using Selenium

    Scenario: taxonomy.feature 8. Refresh
        Using selenium
        Given I am instructor_one in Sample Course

        # shortcut to taxonomy
        When I access the url "/taxonomy/"
        Given the taxonomy workspace is loaded
        I see "Create Concept"

        # Create a taxonomy
        When I create a new concept
        I name the concept "Colors"
        I create the concept
        Then there is a "Colors" concept

        When I click the Import button
        And specify the onomy url
        And confirm the onomy import
        
        Then there is a "Black" term
        Then there is a "Blue" term
        Then there is a "Green" term
        Then there is a "Pastels" term
        Then there is a "Purple" term
        Then there is a "Red" term

        Then there is a "Pastels" concept
        When I click the "Pastels" concept
        Then there is a "Light Blue" term
        Then there is a "Light Green" term
        Then there is a "Pink" term

        Then I click the "Colors" concept
        Then I click the Edit button
        And specify the refresh onomy url
        And confirm the onomy import
        Then there is a "Black" term
        Then there is a "Blue" term
        Then there is a "Green" term
        Then there is a "Pastels" term
        Then there is a "Purple" term
        Then there is a "Red" term

        Then there is a "Pastels" concept
        When I click the "Pastels" concept
        Then there is a "Light Blue" term
        Then there is a "Light Green" term
        Then there is a "Pink" term

        Then there is a "Neons" concept
        When I click the "Neons" concept
        Then there is a "Laser Blue" term
        
        Finished using Selenium
