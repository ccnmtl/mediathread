Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Instructor Course Sources', () => {

    before(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
    });

    it('should check Sources page functionality', () => {
        cy.log('should navigate to Sources page');
        cy.get('a[href*="settings"]').click();
        cy.get('a[href*="sources"]').click();
        cy.url().should('match', /course\/1\/dashboard\/sources\/$/);

        cy.log('should add YouTube as a source to the class');
        cy.get('#youtube').scrollIntoView().should('be.visible');
        cy.get('#youtube').click();
        cy.get('#youtube').should('have.value', 'Remove');
    });
});

describe('Removing Course Source', () => {

    before(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/dashboard/settings/');
        cy.get('a[href*="sources"]').should('be.visible');
        cy.get('a[href*="sources"]').click();
    });

    it('should remove YouTube as a source to the class', () => {
        cy.get('.collection-link').contains('YouTube')
            .scrollIntoView().should('be.visible');
        cy.get('#youtube').scrollIntoView().should('be.visible');
        cy.get('#youtube').should('have.value', 'Remove')
            .click();
        cy.get('#youtube').should('not.exist');
    });
});
