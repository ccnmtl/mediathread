describe('Course Navigation', () => {
    it('Logs in as instructor_one and navigates to a course', () => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.url().should('match', /course\/1\/$/);
        cy.checkPageA11y();
    });
});
