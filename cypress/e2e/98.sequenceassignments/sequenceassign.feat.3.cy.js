describe('Sequence Assignment Feat: Instructor adds feedback', () => {

    before(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
    });

    it('should add and edits feedback', () => {

        cy.get('#cu-privacy-notice-button').click({force: true});
        cy.visit('/course/1/assignments/');
        cy.contains('Test Sequence Assignment').click();
        cy.get('#student-response-dropdown').click();
        cy.contains('Student One').click();
        cy.title().should('contain', 'Test Sequence Assignment | Mediathread');
        cy.contains('Feedback').click();
        cy.getIframeBody().find('p').click().type('Example feedback');
        cy.get('.save-feedback').click({force: true});
        cy.get('.alert-success').should('contain', 'Your feedback was saved');
        cy.contains('Save Feedback').click({force: true});

    });
});
