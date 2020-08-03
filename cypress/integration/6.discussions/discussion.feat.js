Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Discussion View: Create Discussion', () => {

    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-title a').contains('MAAP Award Reception');
    });

    it('Instructor Creates Discussion', () => {
        cy.visit('/course/1/assignments/');

        cy.log('Create a discussion');
        cy.get('button').contains('Add an assignment').should('be.visible');
        cy.get('button').contains('Add an assignment').click()
        cy.get('#discussion-assignment-card').should('be.visible');
        cy.get('#discussion-assignment-card button')
            .contains('Add Assignment').click()

        cy.log('create discussion');
        cy.get('#cu-privacy-notice-icon').click();
        //TODO: test discussion creation from homepage
        cy.title().should('contain', 'Discussion');
        cy.getIframeBody().find('p').click()
            .type('Adding a comment');
        cy.get('#comment-form-submit').click();
        cy.get('.respond_prompt').should('be.visible');
        cy.get('.edit_prompt').contains('Edit').should('be.visible');

        cy.visit('/course/1/oldhome/');
        cy.get('#loaded').should('exist');
        cy.contains('Discussion Title').should('have.attr', 'href');
        cy.contains('Discussion Title').click();
        cy.title().should('contain', 'Discussion');
    });
});
