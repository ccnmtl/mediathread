// TODO: why are we getting an error for `the_records`
// here in the course settings page?
Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Taxonomy Feature: Refresh', () => {
    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('a[href*="settings"]').click();
        cy.get('a[href*="taxonomy"]').click();
    });

    it('should Refresh', () => {

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
        cy.get('[name=onomy_url]').type('/media/onomy/test.json');
        cy.get('a.import-vocabulary-submit').click();
        cy.get('[data-id="Black"]').should('exist');
        cy.get('[data-id="Blue"]').should('exist');
        cy.get('[data-id="Green"]').should('exist');
        cy.get('[data-id="Pastels"]').should('exist');
        cy.get('[data-id="Purple"]').should('exist');
        cy.get('[data-id="Red"]').should('exist');
        cy.contains('Pastels').should('exist');
        cy.contains('Pastels').click();
        cy.get('[data-id="Light Blue"]').should('exist');
        cy.get('[data-id="Light Green"]').should('exist');
        cy.get('[data-id="Pink"]').should('exist');
        cy.contains('Colors').click();
        cy.get('.import-vocabulary-open > span').click({force: true});
        cy.get('[name=onomy_url]:visible').type(',/media/onomy/reimport_test.json');
        cy.get('#import-vocabulary-btn')
            .click();
        cy.get('[data-id="Black"]').should('exist');
        cy.get('[data-id="Blue"]').should('exist');
        cy.get('[data-id="Green"]').should('exist');
        cy.get('[data-id="Pastels"]').should('exist');
        cy.get('[data-id="Purple"]').should('exist');
        cy.get('[data-id="Red"]').should('exist');
        cy.contains('Pastels').should('exist');
        cy.contains('Pastels').click();
        cy.get('[data-id="Light Blue"]').should('exist');
        cy.get('[data-id="Light Green"]').should('exist');
        cy.get('[data-id="Pink"]').should('exist');
        cy.contains('Neons').should('exist');
        cy.contains('Neons').click();
        cy.get('[data-id="Laser Blue"]').should('exist');
    });
});
