describe('Instructor Feat: Students are forbidden', () => {

    beforeEach(() => {
        cy.login('student_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');
    });

    it('Manage sources should be forbidden', () => {
        cy.visit('/course/1/dashboard/sources/', {failOnStatusCode: false});
        cy.contains('forbidden').should('be.visible');
    });

    it('Publishing settings should be forbidden', () => {
        cy.visit('/course/1/dashboard/settings/', {failOnStatusCode: false});
        cy.contains('forbidden').should('be.visible');
    });

    it('Taxonomy should be forbidden', () => {
        cy.visit('/course/1/taxonomy/', {failOnStatusCode: false});
        cy.contains('forbidden').should('be.visible');
    });

    it('Reports should be forbidden', () => {
        cy.visit('/reports/class_assignments/', {failOnStatusCode: false});
        cy.contains('forbidden').should('be.visible');
        cy.visit('/reports/class_activity/', {failOnStatusCode: false});
        cy.contains('forbidden').should('be.visible');
        cy.visit('/reports/class_summary', {failOnStatusCode: false});
        cy.contains('forbidden').should('be.visible');
    });
});
