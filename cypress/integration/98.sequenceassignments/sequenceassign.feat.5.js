Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Sequence Assignment Feat: Student reviews Student Response', () => {

    before(() => {
        cy.login('student_two', 'test');
        cy.visit('/course/1/');
    });

    it('should review feedback', () => {
        cy.get('#cu-privacy-notice-button').click({force: true});
        cy.visit('/course/1/assignments/');
        cy.contains('Test Sequence Assignment').parent('tr').within(() => {
            // all searches are automatically rooted to the found tr element
            cy.get('td').eq(2).contains('Test Sequence Assignment');
            cy.get('td').eq(1).contains('No Response');
            cy.get('td').eq(3).contains('Add Response');
            cy.get('td').eq(4).contains('Sequence');

            cy.get('td').eq(3).contains('Add Response').click();
        });
        cy.get('#assignment-responses').click();
        cy.contains('One, Student').click();
        cy.get('.assignment-response-title')
            .should('contain', 'Example response');
        cy.get('.assignment-response-author').should('contain', 'Student One');
    });
});
