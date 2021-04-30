describe('Taxonomy Feature', () => {
    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('a[href*="settings"]').click();
        cy.get('a[href*="taxonomy"]').click();
    });

    it('should Create, Duplicate, Delete Taxonomy', () => {

        cy.log('Vocabulary page');
        cy.title().should('include', 'Course Vocabulary Workspace');
        cy.get('#loaded').should('exist');
        cy.get('#cu-privacy-notice-button').click();
        cy.get('#new-vocabulary').should('exist');

        cy.log('create a taxonomy');
        cy.get('a.create-vocabulary-open').click();
        cy.get('input.create-vocabulary-name')
            .should('have.attr', 'placeholder', 'Concept name');

        cy.log('name and save');
        cy.get('.create-vocabulary-name').type('Colors');
        cy.get('.create-vocabulary-submit').click();
        cy.contains('Colors').should('exist');
        cy.get('.create-vocabulary').should('exist')
            .and('contain', 'Create Concept');
        cy.contains('Colors Concept').should('exist');
        cy.contains('Terms').should('exist');
        cy.get('.col-md-10 > .form-control')
            .should('have.attr', 'placeholder', 'Type new term name here');

        cy.log('duplicate taxonomy');
        cy.get('a.create-vocabulary-open').click();
        cy.get('.create-vocabulary-name').type('Colors');
        cy.get('.create-vocabulary-submit').click();
        cy.get('#dialog-confirm').should('contain',
            'A Colors concept exists. Please choose another name');
    });

    it('delete the taxonomy', () => {
        cy.get('.delete_icon').should('exist');
        cy.get('.delete_icon').click();
        cy.get('.ui-dialog-buttonset > :nth-child(2)').click();
        cy.contains('Colors').should('not.be', 'visible');
    });
});
