// // TODO: why are we getting an error for `the_records`
// // here in the course settings page?
// Cypress.on('uncaught:exception', (err, runnable) => {
//     // returning false here prevents Cypress from
//     // failing the test
//     return false;
// });
//
// describe('Course Settings', function() {
//
//     beforeEach(function() {
//         cy.login('instructor_one', 'test');
//         cy.visit('/course/1/');
//         // Click Course Settings
//         cy.get('a[href*="settings"]').click();
//     });
//
//     it('navigates to the Course Settings page', function() {
//       cy.url().should('match', /course\/1\/dashboard\/settings\/$/);
//     });
//
//     it('has its publish to world option off by default', function() {
//         cy.get('input#id_publish_to_world').should('not.be.checked');
//     });
//
//     it('has publish options set to yes', function() {
//         cy.get('input#id_publish_to_world').click();
//         cy.get('.btn-primary').click();
//         cy.wait(500);
//         cy.get('input#id_publish_to_world').should('be.checked');
//     });
//
//     it('has item and selection visibility "on" by default', function() {
//         cy.url().should('match', /course\/1\/dashboard\/settings\/$/);
//         cy.get('input#id_see_eachothers_items').should('be.checked');
//         cy.get('input#id_see_eachothers_selections').should('be.checked');
//     });
//
//     it('changes selection visibility to "off"', function() {
//         cy.url().should('match', /course\/1\/dashboard\/settings\/$/);
//         cy.get('input#id_see_eachothers_items').click();
//         cy.get('input#id_see_eachothers_selections').click();
//         cy.get('.btn-primary').click();
//         cy.get('input#id_see_eachothers_selections').should('not.be.checked');
//         cy.get('input#id_see_eachothers_items').should('not.be.checked');
//     });
// });
