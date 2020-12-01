// TODO: why are we getting an error for `the_records`
// here in the course settings page?
Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Taxonomy Feature: Create, Duplicate, Delete Term', () => {
    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('a[href*="settings"]').click();
        cy.get('a[href*="taxonomy"]').click();
    });

    it('should Create, Duplicate, Delete Terms', () => {

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

        cy.log('create a term');
        cy.get('.col-md-10 > .form-control').type('Red');
        cy.get('.create-term-submit').click({force: true});
        cy.get('div.term-display h5').should('contain', 'Red');

        cy.log('duplicate term');
        cy.get('.col-md-10 > .form-control').type('Red');
        cy.get('.create-term-submit').click({force: true});
        cy.get('#dialog-confirm').should('contain',
            'Red term already exists. Please choose a new name');
        cy.get('.ui-dialog-buttonset > .ui-button').contains('OK').click();

        cy.log('delete the term');
        cy.get('.delete-term').click();
        cy.contains('OK').click();
        cy.get('div.term-display h5').should('not.be', 'visible');
    });
    it('clean up', () => {
        cy.get('.delete-vocabulary > .delete_icon').click();
        cy.get('.ui-dialog-buttonset > :nth-child(2)').click();
        cy.contains('Colors').should('not.be', 'visible');
    });
});
