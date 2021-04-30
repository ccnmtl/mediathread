describe('Taxonomy Feature: Edit', () => {
    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('a[href*="settings"]').click();
        cy.get('a[href*="taxonomy"]').click();
    });

    it('should Create, Duplicate, Delete Taxonomy', () => {

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

        cy.log('edit the taxonomy');
        cy.get('.edit_icon').should('exist');
        cy.get('.edit_icon').click({force: true});

        cy.log('name and save');
        cy.focused('input[name="display_name"]').clear();
        cy.focused('input[name="display_name"]').type('Shapes');
        cy.get('.edit-vocabulary-submit').click({force: true});
        cy.contains('Shapes').should('exist');
        cy.contains('Colors').should('not.exist');
    });
    it('clean up', () => {
        cy.get('.delete_icon').click();
        cy.get('.ui-dialog-buttonset > :nth-child(2)').click();
        cy.contains('Shapes').should('not.be', 'visible');
    });
});
