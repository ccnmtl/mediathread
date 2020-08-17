Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Assignment Feature: Instructor View', () => {

    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');
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
        cy.get('[data-cy="assignment-visibility"]')
            .contains('Shared with Class').should('be.visible');
        cy.get('#student-response-dropdown')
            .contains('1 of 3 students responded').should('be.visible');
        cy.get('#assignment-responses').should('not.be.visible');
        cy.get('#instructions-heading-one')
            .contains('Instructions').should('be.visible');
        cy.get('#response-heading-one').should('not.exist');
        cy.get('#feedback-heading-one').should('not.exist');
        cy.get('#instructions').should('be.visible');

        cy.log('Select student response');
        cy.get('#student-response-dropdown').click()
        cy.get('a.dropdown-item').contains('Student One').click();

        cy.log('View the response');
        cy.title().should('include', 'Mediathread Sample Assignment Response');
        cy.get('#instructions').should('not.be.visible');
        cy.get('.btn-edit-assignment').should('exist');
        cy.get('#assignment-responses').should('not.be.visible');
        cy.get('[data-cy="response-visibility"]')
            .contains('Shared with Instructor').should('be.visible');

        cy.get('#student-response-dropdown')
            .contains('1 of 3 students responded').should('be.visible');
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
        cy.get('#student-response-dropdown')
            .contains('1 of 3 students responded').should('be.visible');
        cy.get('#assignment-responses').should('not.be.visible');
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
        cy.get('[data-cy="assignment-visibility"]').should('not.exist');
        cy.get('#response').should('not.be.visible');
        cy.get('[data-cy="response-visibility"]')
            .contains('Shared with Instructor')
            .should('exist').should('not.be.visible');
        cy.get('#assignment-responses').should('not.be.visible');
        cy.get('#student-responses').should('not.be.visible');
        cy.get('#instructions-heading-one').should('be.visible');
        cy.get('#response-heading-one').should('be.visible');
        cy.get('#feedback-heading-one').should('be.visible');
        cy.get('#feedback').contains('Amazing Response');
    });
});
