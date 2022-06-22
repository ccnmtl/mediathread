describe('Instructor Feat: Test Assignment Responses', () => {
    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');
    });

    it('should test assignment response as an instructor', () => {

        cy.get('a[href="/course/1/dashboard/settings/"]').click();
        cy.title().should('contain', 'Manage Course');
        cy.get('a[href="/course/1/reports/class_assignments/"]').click();
        cy.contains('1 / 3').should('have.attr', 'href');
        cy.contains('1 / 3').click();
        cy.contains('Assignment Responses | Sample Assignment').should('exist');
        cy.contains('Student One').should('exist');
        cy.contains('Sample Assignment Response').should('have.attr', 'href');
        cy.contains('Shared with Instructor').should('exist');
        cy.contains('No').should('exist');

        cy.contains('Sample Assignment Response').click();
        cy.title().should('contain', 'Sample Assignment Response');
    });
});
