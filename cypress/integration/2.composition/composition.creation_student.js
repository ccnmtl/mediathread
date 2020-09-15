// TODO: why are we getting an error for `the_records`
// here in the course settings page?
Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Student Creates Composition', () => {

    beforeEach(() => {
        cy.login('student_one', 'test');
        cy.visit('/course/1/');
        cy.wait(500);
    });

    it('should create a Composition as a Student', () => {
        cy.log('should check composition panel edit features');

        cy.visit('/course/1/projects');
        cy.get('.page-title').contains('Projects');
        cy.get('#cu-privacy-notice-icon').click();
        cy.get('button#add-composition-button').click();

        cy.get('a.nav-link.active').contains('Projects');
        cy.get('.breadcrumb-item').contains('Back to all projects');

        cy.get('.page-title').should('be.visible');
        cy.get('.page-title').contains('Untitled')
        cy.contains('ul', 'Student One').should('exist');
        cy.get('.project-visibility-description')
            .contains('Draft').should('exist');
        cy.get('.project-revisionbutton').should('exist');
        cy.get('.project-editbutton.active').should('exist');
        cy.get('.project-previewbutton.active').should('not.exist');
        cy.get('.project-savebutton').should('exist');
        cy.get('.project-submitbutton').should('exist');
        cy.get('.participant-container').should('be', 'visible');
        cy.get('select[name="participants"]').should('exist');
        cy.get('select[name="participants"]').should('not.be.visible');

        cy.log('should save a composition');
        cy.get('.page-title').click().clear()
            .type('Composition: Scenario 2');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');
        cy.get('.project-savebutton').click();
        cy.get('.project-savebutton').should('contain', 'Saved');

        cy.log('should toggle preview mode');
        cy.get('.project-previewbutton').click();
        cy.get('.project-revisionbutton').should('exist');
        cy.get('.project-editbutton.active').should('not.exist');
        cy.get('.project-previewbutton.active').should('exist');
        cy.get('.project-savebutton').should('contain', 'Saved');
        cy.get('.participant-container').should('be', 'visible');
    });

    it('should show on projects page', () => {
        cy.visit('/course/1/projects/');
        cy.contains('Composition: Scenario 2').parent('td').parent('tr').within(() => {
            // all searches are automatically rooted to the found tr element
            cy.get('td').eq(2).contains('Composition: Scenario 2');
            cy.get('td').eq(1).contains('Draft');
            cy.get('td').eq(0).contains('Student One');
            cy.get('td').eq(3).contains('Composition');
            cy.get('td').eq(5).contains('Delete');
        });
    });

});
