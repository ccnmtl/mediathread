// TODO: why are we getting an error for `the_records`
// here in the course settings page?
Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Instructor Creates Composition', () => {
    beforeEach(() => {
        cy.visit('/course/1/');
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-title a').contains('MAAP Award Reception');
    });

    it('should create a composition as an Instructor', () => {

        cy.log('creates a project');
        cy.visit('/course/1/projects');
        cy.get('.page-title').contains('Projects');
        cy.get('#cu-privacy-notice-icon').click();
        cy.get('button#add-composition-button').click();

        cy.log('should check composition panel features');
        cy.get('.page-title').should('be.visible');
        cy.get('.page-title').contains('Untitled')
        cy.contains('ul', 'Instructor One').should('exist');
        cy.get('.project-visibility-description').contains('Draft')
            .should('exist');
        cy.get('.project-revisionbutton').should('exist');
        cy.get('.project-editbutton.active').should('exist');
        cy.get('.project-previewbutton.active').should('not.exist');
        cy.get('.project-savebutton').should('exist');
        cy.get('select[name="participants"]').should('exist');
        cy.get('select[name="participants"]').should('not.be.visible');
        cy.get('.participant-container').should('be.visible');

        cy.log('write title and text and save composition');
        cy.get('.page-title').click().clear()
            .type('Composition: Scenario 1');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');

        cy.log('Save the project');
        cy.get('div.ajaxloader').should('not.be.visible');
        cy.get('#id_publish').should('not.be.visible');
        cy.get('.btn-save-project').should('not.be.visible');
        cy.get('.project-savebutton').contains('Save').should('be.visible');
        cy.get('.project-savebutton').click();

        cy.get('.save-publish-status.modal').should('be.visible');
        cy.get('.save-publish-status.modal #id_publish').find('li')
            .should('contain', 'Draft - only you can view')
            .should('be.visible');
        cy.get('.save-publish-status.modal input[name=publish]:checked')
            .should('exist').should('be.visible');
        cy.get('.save-publish-status.modal #id_publish').find('li')
            .should('contain', 'Whole Class - all class members can view')
            .should('be.visible');
        cy.get('.save-publish-status.modal #id_publish').find('li')
            .should('not.contain', 'Whole World - a public url is provided')
            .should('be.visible');
        cy.get('.btn-save-project').should('be.visible');
        cy.get('.btn-save-project').click();
        cy.get('.btn-save-project').should('not.be.visible');

        cy.get('.project-savebutton').contains('Saved').should('exist');
        cy.get('#id_publish').should('not.be.visible');
        cy.get('.btn-save-project').should('not.be.visible');

        cy.log('toggle preview mode');
        cy.get('.project-previewbutton').click();
        cy.get('.project-revisionbutton').should('exist');
        cy.get('.project-editbutton.active').should('not.exist');
        cy.get('.project-previewbutton.active').should('exist');
        cy.get('.project-savebutton').should('contain', 'Saved');
        cy.get('.participant-container').should('be.visible');
    });

    it('should show on projects page', () => {
        cy.visit('/course/1/projects/');
        cy.get('#cu-privacy-notice-icon').click();
        cy.contains('Composition: Scenario 1').parent('td').parent('tr').within(() => {
            // all searches are automatically rooted to the found tr element
            cy.get('td').eq(0).contains('Composition: Scenario 1');
            cy.get('td').eq(1).contains('Draft');
            cy.get('td').eq(2).contains('Instructor One');
            cy.get('td').eq(3).contains('Composition');
            cy.get('td').eq(5).contains('Delete');
        });
    });

});
