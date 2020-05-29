describe('Log In', function() {
    it('Logs in as instructor_one', function() {
      cy.visit('http://localhost:8000');
      cy.get('#guest-login').click();
      cy.get('#login-local>div.login-local-form').should('be.visible');
      cy.get('#id_username').type('instructor_one').blur();
      cy.get('#id_password').type('test').blur();
      cy.get('#login-local input[type="submit"]').click();
      cy.get('#course_information').contains('My Courses');
    });
});
