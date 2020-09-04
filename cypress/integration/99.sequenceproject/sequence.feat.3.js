Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Sequence Project Feat: Other Student Can View', () => {

    before(() => {
        cy.login('student_two', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');
    });

    it('Student Views Sequence Project', () => {
        cy.get('#projects-list').click();
        cy.get('#cu-privacy-notice-icon').click();
        cy.get('#select-owner').select('One, Student');
        cy.contains('Example project').should('exist');
        cy.contains('Example project').click();
        cy.get('.assignment-response-title')
            .should('contain', 'Example project');
        cy.get('.assignment-response-author').should('contain', 'Student One');
    });
});
