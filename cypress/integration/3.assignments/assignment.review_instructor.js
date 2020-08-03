Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Assignment Feature: Instructor View', () => {

    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-title a').contains('MAAP Award Reception');
    });

    it('Reviews the assignment', () => {
        cy.log('visit the assignments page');
        cy.get('#cu-privacy-notice-icon').click();
        cy.visit('/course/1/assignments/');

        cy.contains('1 / 3').parent('tr').within(() => {
            // all searches are automatically rooted to the found tr element
            cy.get('a').contains('Sample Assignment').click();
        });

        cy.title().should('include', 'Mediathread Sample Assignment');
        cy.get('.btn-edit-assignment').should('exist');
        cy.get('.project-visibility-description').contains('Shared with Class');
        cy.get('#assignment-responses').should('not.be.visible');
        cy.get('#student-responses').should('be.visible');
        cy.get('#instructions-heading-one')
            .contains('Instructions').should('be.visible');
        cy.get('#response-heading-one').should('not.exist');
        cy.get('#feedback-heading-one').should('not.exist');

        cy.log('Select student response');
        cy.get('#student-responses').select('Student One');

        cy.log('View the response');
        cy.title().should('include', 'Mediathread Sample Assignment Response');
        cy.get('.btn-edit-assignment').should('exist');
        cy.get('.project-visibility-description').contains('Shared with Class');
        cy.get('#assignment-responses').should('not.be.visible');
        cy.get('#student-responses').should('be.visible');
        cy.get('#instructions-heading-one')
            .contains('Instructions').should('be.visible');
        cy.get('#response-heading-one').should('be.visible');
        cy.get('#feedback-heading-one').should('not.exist');
        cy.wait(500);

        cy.log('Add feedback');
        cy.get('button').contains('Add Feedback').click();
        cy.title().should('include', 'Mediathread Sample Assignment Response');
        cy.get('#loaded').should('exist');
        cy.get('.btn-edit-assignment').should('exist');
        cy.get('.project-visibility-description').contains('Shared with Class');
        cy.get('#assignment-responses').should('not.be.visible');
        cy.get('#student-responses').should('be.visible');
        cy.get('#instructions-heading-one')
            .contains('Instructions').should('be.visible');
        cy.get('#response-heading-one').should('be.visible');
        cy.get('#feedback-heading-one').should('be.visible');
        cy.getIframeBody().find('p').click()
            .type('Amazing Response');
        cy.get('#comment-form-submit').click();

        cy.log('View as student');
        cy.login('student_one', 'test');
        cy.visit('/course/1/assignments/');
        cy.get('a').contains('View Feedback').click();

        cy.title().should('include', 'Mediathread Sample Assignment Response');
        cy.get('.btn-edit-assignment').should('not.exist');
        cy.get('.project-visibility-description').should('not.exist');
        cy.get('#assignment-responses').should('not.be.visible');
        cy.get('#student-responses').should('not.be.visible');
        cy.get('#instructions-heading-one').should('be.visible');
        cy.get('#response-heading-one').should('be.visible');
        cy.get('#feedback-heading-one').should('be.visible');
        cy.get('#feedback').contains('Amazing Response');
    });
});
