Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Sequence Assignment Feat: Student reviews feedback', () => {

    before(() => {
        cy.login('student_one', 'test');
        cy.visit('/course/1/');
    });

    it('should review feedback', () => {

        //TODO: use the UI to navigate to the Sample Selection Assignment page
        cy.get('#cu-privacy-notice-button').click({force: true});
        cy.visit('/course/1/assignments/');
        cy.contains('Test Sequence Assignment').parent('tr').within(() => {
            // all searches are automatically rooted to the found tr element
            cy.get('td').eq(2).contains('Test Sequence Assignment');
            cy.get('td').eq(1).contains('Shared with Class');
            cy.get('td').eq(3).contains('View Feedback');
            cy.get('td').eq(4).contains('Sequence');

            cy.get('td').eq(3).contains('View Feedback').click();
        });
        cy.contains('Feedback').click({force: true});
        cy.contains('Example feedback').should('exist');
    });
});
