Feature: Taxonomy

    #Scenario: taxonomy.feature 1. Create Taxonomy
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
        
    #Scenario: taxonomy.feature 2. Duplicate Taxonomy
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
        
    #Scenario: taxonomy.feature 3. Delete Taxonomy
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
        
    #Scenario: taxonomy.feature 4. Edit Taxonomy
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

    #Scenario: taxonomy.feature 5. Create Term
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
        Then There is a "Red" term
        
    #Scenario: taxonomy.feature 6. Duplicate Term
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
        Then There is a "Red" term
        
        # Duplicate term
        When I name a term "Red"
        And create the term
        Then I'm told "Red term already exists. Please choose a new name"
        
    #Scenario: taxonomy.feature 7. Delete Term
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
        Then There is a "Red" term

        # Delete the term
        When I click the "Red" term delete icon
        And I confirm the action
        Then there is no "Red" term
        
                 
    #Scenario: taxonomy.feature 8. Edit Term
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
        Then There is a "Red" term

        # Edit the term
        When I click the "Red" term edit icon
        I rename the "Red" term to "Blue"
        I save the term
        I wait until the "Red" rename is complete

        Then There is a "Blue" term
        Then there is no "Red" term

    #Scenario: taxonomy.feature 9. Create from onomy
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

        When I click the Import button
        And specify the onomy url
        And confirm the onomy import

        Then There is a "Black" term
        Then There is a "Blue" term
        Then There is a "Green" term
        Then There is a "Pastels" term
        Then There is a "Purple" term
        Then There is a "Red" term

        Then there is a "Pastels" link
        When I click the "Pastels" link
        Then There is a "Light Blue" term
        Then There is a "Light Green" term
        Then There is a "Pink" term

        Finished using Selenium

    #Scenario: taxonomy.feature 10. onomy delete and refresh
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

        When I click the Import button
        And specify the onomy url
        And confirm the onomy import

        Then There is a "Black" term
        Then There is a "Blue" term
        Then There is a "Green" term
        Then There is a "Pastels" term
        Then There is a "Purple" term
        Then There is a "Red" term

        Then there is a "Pastels" link
        When I click the "Pastels" link
        Then There is a "Light Blue" term
        Then There is a "Light Green" term
        Then There is a "Pink" term

        Then I click the "Colors" link
        When I click the "Red" term delete icon
        Then there is no "Red" term
        
        When I click the "Colors" link
        Then I click the Refresh button
        
        Then There is a "Red" term

        Finished using Selenium

    #Scenario: taxonomy.feature 11. Try invalid Onomy url
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

    Scenario: taxonomy.feature 12. Refresh
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

        When I click the Import button
        And specify the onomy url
        And confirm the onomy import

        Then There is a "Black" term
        Then There is a "Blue" term
        Then There is a "Green" term
        Then There is a "Pastels" term
        Then There is a "Purple" term
        Then There is a "Red" term

        Then There is a "Pastels" link
        When I click the "Pastels" link
        Then There is a "Light Blue" term
        Then There is a "Light Green" term
        Then There is a "Pink" term

        Then I click the "Colors" link
        Then I click the Edit button
        And specify the refresh onomy url
        And confirm the onomy import

        Then There is a "Black" term
        Then There is a "Blue" term
        Then There is a "Green" term
        Then There is a "Pastels" term
        Then There is a "Purple" term
        Then There is a "Red" term
        #Then There is a "Neons" term

        Then There is a "Pastels" link
        When I click the "Pastels" link
        Then There is a "Light Blue" term
        Then There is a "Light Green" term
        Then There is a "Pink" term

        Then there is a "Neons" link
        When I click the "Neons" link
        Then There is a "Laser Blue" term

        Finished using Selenium
