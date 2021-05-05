Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Taxonomy Feature: Try invalid Onomy url', () => {
    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('a[href*="settings"]').click();
        cy.get('a[href*="taxonomy"]').click();
    });

    it('should try invalid Onomy url', () => {

        cy.log('shortcut to taxonomy');
        cy.title().should('include', 'Course Vocabulary Workspace');
        cy.get('#loaded').should('exist');
        cy.get('#cu-privacy-notice-button').click({force: true});
        cy.get('#new-vocabulary').should('exist');

        cy.log('create a taxonomy');
        cy.get('a.create-vocabulary-open').click({force: true});
        cy.get('input.create-vocabulary-name').type('Colors');
        cy.get('.create-vocabulary-submit').click({force: true});
        cy.contains('Colors').should('exist');
        cy.contains('Import').click();
        cy.get('[name=onomy_url]').type('incorrect');
        cy.get('a.import-vocabulary-submit').click();
        cy.get('[data-id="Black"]').should('not.exist');
        cy.get('[data-id="Blue"]').should('not.exist');
        cy.get('[data-id="Green"]').should('not.exist');
        cy.get('[data-id="Pastels"]').should('not.exist');
        cy.get('[data-id="Purple"]').should('not.exist');
        cy.get('[data-id="Red"]').should('not.exist');
    });
    it('clean up', () => {
        cy.get('.delete_icon').click();
        cy.get('.ui-dialog-buttonset > :nth-child(2)').click();
        cy.contains('Colors').should('not.be', 'visible');
    });
});
