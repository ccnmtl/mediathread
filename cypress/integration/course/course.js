describe('Course Navigation', function() {
    it('Logs in as instructor_one and navigates to a course', function() {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.url().should('match', /course\/1\/$/);
    });
});
