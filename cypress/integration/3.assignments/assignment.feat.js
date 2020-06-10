Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Assignment Feature', () => {

    beforeEach(() => {
        //cy.restoreLocalStorage();
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
    });

    it('navigates to home page', () => {
        cy.url().should('match', /course\/1\/$/);
    });
    it('creates an assignment & navigate to assignment workspace', () => {
        cy.get('#homepage-create-menu').click();
        cy.contains('Create Composition Assignment')
            .should('exist')
            .click();
        cy.url().should('match', /project\/view\/1\/$/);
        cy.get('#loaded').should('exist');
        cy.get('.panel-subcontainer-title').contains('Untitled');
        cy.get('.panel-container.open.assignment').should('exist');
        cy.get('.project-savebutton').should('exist');
        cy.get('.project-visibility-description').contains('Draft');
        cy.get('.panel-subcontainer-title input[type=text]').clear()
            .type('Assignment: Scenario 1');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');
        cy.get('.project-savebutton').click();
        cy.contains('Whole Class - all class members can view').click();
        cy.get('.btn-primary').contains('Save').click();
        cy.get('.project-visibility-link')
            .should('contain', 'Published to Class');
        cy.get('.panel-container.open.assignment').should('exist');
        cy.get('.project-savebutton').should('contain', 'Saved');
        cy.contains('Assignment: Scenario 1');
    });
});
