describe('Sequence Project Feat: Instructor Can View', () => {

    before(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');
    });

    it('Instructor Views Sequence Project', () => {
        cy.get('#projects-list').click();
        cy.get('#cu-privacy-notice-button').click();
        cy.get('#select-owner').select('One, Student');
        cy.contains('Example project').should('exist');
        cy.contains('Example project').click();
        cy.get('.assignment-response-title')
            .should('contain', 'Example project');
        cy.get('.assignment-response-author').should('contain', 'Student One');
    });
});
