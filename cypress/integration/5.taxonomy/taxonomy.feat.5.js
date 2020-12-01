// TODO: why are we getting an error for `the_records`
// here in the course settings page?
Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Taxonomy Feature: Create Term, Edit Taxonomy', () => {
    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('a[href*="settings"]').click();
        cy.get('a[href*="taxonomy"]').click();
    });

    it('should create term and edit Taxonomy', () => {

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

        cy.log('create term');
        cy.get('.col-md-10 > .form-control').type('Red');
        cy.get('.create-term-submit').click({force: true});
        cy.get('div.term-display h5').should('contain', 'Red');

        cy.log('edit the taxonomy');
        cy.get('.edit-vocabulary-open > .edit_icon').should('exist');
        cy.get('.edit-vocabulary-open > .edit_icon').click({force: true});

        cy.log('name and save');
        cy.focused('input[name="display_name"]').clear();
        cy.focused('input[name="display_name"]').type('Shapes');
        cy.get('.edit-vocabulary-submit').click({force: true});
        cy.contains('Shapes').should('exist');
        cy.contains('Colors').should('not.exist');
    });
    it('clean up', () => {
        cy.get('.delete-vocabulary > .delete_icon').click();
        cy.get('.ui-dialog-buttonset > :nth-child(2)').click();
        cy.contains('Shapes').should('not.be', 'visible');
    });
});
