// TODO: why are we getting an error for `the_records` 
// here in the course settings page?
Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
})

describe('Course Settings', function() {
    it('has its publish to world option off by default', function() {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.url().should('match', /course\/1\/$/);

        // Click Course Settings
        cy.get('a[href*="settings"]').click();
        cy.url().should('match', /course\/1\/dashboard\/settings\/$/);

        cy.get('input#id_publish_to_world').scrollIntoView();
        cy.get('input#id_publish_to_world').should('not.be.checked');
    });
});
