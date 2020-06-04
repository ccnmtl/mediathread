// // TODO: why are we getting an error for `the_records`
// // here in the course settings page?
// Cypress.on('uncaught:exception', (err, runnable) => {
//     // returning false here prevents Cypress from
//     // failing the test
//     return false;
// });
//
// describe('Instructor Course Sources', function() {
//
//     beforeEach(function () {
//         cy.login('instructor_one', 'test');
//         cy.visit('/course/1/');
//         cy.get('a[href*="settings"]').click();
//         cy.get('a[href*="sources"]').click();
//     });
//
//     it('should navigate to Sources page', function() {
//         cy.url().should('match', /course\/1\/dashboard\/sources\/$/);
//     });
//
//     it('should add YouTube as a source to the class', function() {
//         cy.get('#youtube').click();
//         cy.get('#youtube').should('have.value', 'Remove');
//     });
//
//     it('should show YouTube as a source', function() {
//       cy.visit('/course/1/');
//       cy.get('.recommend_source').contains('YouTube').should('exist');
//     });
// });
//
// describe('Student Course Sources', function() {
//
//     before(function() {
//         cy.login('student_one', 'test');
//         cy.visit('/course/1');
//     });
//
//     it('should show YouTube as a source, as a Student', function() {
//         cy.get('.recommend_source').contains('YouTube').should('exist');
//     });
// });
//
// describe('Removing Course Source', function() {
//
//     beforeEach(function() {
//         cy.login('instructor_one', 'test');
//         cy.visit('/course/1');
//         cy.get('a[href*="settings"]').click();
//         cy.get('a[href*="sources"]').click();
//     });
//
//     it('should remove YouTube as a source to the class', function() {
//         cy.get('input#youtube.btn.btn-default')
//           .should('have.value', 'Remove')
//           .click();
//         cy.contains('Remove').should('not.exist');
//     });
//
//     it('should should not show any recommended source', function() {
//         cy.visit('/course/1/');
//         cy.get('.recommend_source').should('not.exist');
//   });
// });
