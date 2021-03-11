Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Selection Assignment Feat: Instructor adds & edits feedback', () => {

    before(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
    });

    it('should add and edits feedback', () => {

        //TODO: use the UI to navigate to the Sample Selection Assignment page
        cy.get('#cu-privacy-notice-button').click({force: true});
        cy.visit('/project/view/2/');
        cy.title().should('contain', 'Sample Selection Assignment');
        cy.contains('1 Responses').should('exist');
        cy.get('.btn-edit-assignment').contains('Edit Assignment')
            .should('be.visible');
        cy.get('span.feedback-count').should('contain', '0');
        cy.get('#addFeedback').should('contain', 'add feedback')
            .click({force: true});
        cy.get('#annotation-feedback-student_one > form > .form-control')
            .type('good job');
        cy.contains('Save Feedback').click({force: true});
        cy.get('#editFeedback').should('contain', 'edit feedback')
            .and('have.attr', 'href');
        cy.get('span.feedback-count').should('contain', '1');
    });
});
