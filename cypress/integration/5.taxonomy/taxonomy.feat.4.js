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

        cy.log('edit term');
        cy.get('.edit-term-open').find('.edit_icon').should('exist');
        cy.get('.edit-term-open').find('.edit_icon').click();
        cy.get('.term-edit > input[name="term_name"]').clear().type('Blue');
        cy.get('.edit-term-submit').click();
        cy.get('input[name="term_name"][value="Blue"]').should('exist');
        cy.get('[data-id="Blue"]').should('exist');
        cy.get('div.term-display h5').should('not.be', 'visible');
    });
    it('clean up', () => {
        cy.get('.delete-vocabulary > .delete_icon').click();
        cy.get('.ui-dialog-buttonset > :nth-child(2)').click();
        cy.contains('Colors').should('not.be', 'visible');
    });
});
