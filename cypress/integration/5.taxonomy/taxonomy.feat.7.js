// TODO: why are we getting an error for `the_records`
// here in the course settings page?
Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Taxonomy Feature: Edit Terms', () => {
    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('a[href*="settings"]').click();
        cy.get('a[href*="taxonomy"]').click();
    });

    it('should Edit terms', () => {

        cy.log('shortcut to taxonomy');
        cy.title().should('include', 'Course Vocabulary Workspace');
        cy.get('#loaded').should('exist');
        cy.get('#cu-privacy-notice-icon').click({force: true});
        cy.get('#new-vocabulary').should('exist');

        cy.log('create a taxonomy');
        cy.get('a.create-vocabulary-open').click({force: true});
        cy.get('#id_display_name').type('Colors');
        cy.get('.create-vocabulary-submit').click({force: true});
        cy.contains('Colors').should('exist');
        cy.contains('Import').click();
        cy.get('#onomy_url').type('/media/onomy/test.json');
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
        cy.get('[data-id="Red"]').should('exist');
        //Should this maybe be placed inside the h5?
        cy.get(':nth-child(11) > .term-display > .term-actions > .delete-term > .delete_icon')
            .click();
        cy.contains('OK').click();
        cy.get('div.term-display h5').should('not.be', 'visible');

        cy.log('refresh from the onomy url');
        cy.contains('Refresh').click();
        cy.get('[data-id="Red"]').should('exist');
    });
    it('clean up', () => {
      cy.get('#vocabulary-wrapper-7 > .vocabulary-display > .actions > .delete-vocabulary > .delete_icon')
            .click();
        cy.get('.ui-dialog-buttonset > :nth-child(2)').click();
        cy.get('#vocabulary-wrapper-8').click();
        cy.get('.delete-vocabulary > .delete_icon').click();
        cy.get('.ui-dialog-buttonset > :nth-child(2)').click();
        cy.contains('Colors').should('not.be', 'visible');
        cy.contains('Pastels').should('not.be', 'visible');
    });
});
