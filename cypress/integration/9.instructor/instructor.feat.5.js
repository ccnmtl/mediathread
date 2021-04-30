describe('Instructor Feat: Student Contributions', () => {
    before(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');
    });

    it('should test assignment response as an instructor', () => {
        cy.get('a[href="/course/1/dashboard/settings/"]').click();
        cy.title().should('contain', 'Manage Course');
        cy.get('a[href="/course/1/reports/class_summary/"]').click();
        cy.contains('Member Contributions');
    });
});
