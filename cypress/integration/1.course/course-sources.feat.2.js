describe('Instructor Course Sources', () => {
    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('a[href*="settings"]').click();
        cy.get('a[href*="sources"]').click();
    });

    it('should navigate to Sources page', () => {
        cy.url().should('match', /course\/1\/dashboard\/sources\/$/);
    });

    it('should add YouTube as a source to the class', () => {
        cy.get('#youtube').click();
        cy.get('#youtube').should('have.value', 'Remove');
    });
});

describe('Removing Course Source', () => {
    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/dashboard/settings/');
        cy.get('a[href*="sources"]').click();
    });

    it('should remove YouTube as a source to the class', () => {
        cy.get('input#youtube.btn.btn-default')
            .should('have.value', 'Remove')
            .click();
        cy.contains('Remove').should('not.exist');
    });
});
