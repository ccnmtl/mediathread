// TODO: why are we getting an error for `the_records`
// here in the course settings page?
Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Instructor Creates Composition', () => {
    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.wait(500);
    });

    it('should create a composition as an Instructor', () => {
        cy.log('should check composition panel features');

        cy.visit('/course/1/project/create/', {
            method: 'POST',
            body: {
                project_type: 'composition'
            }
        });

        cy.wait(500);

        cy.get('#loaded').should('exist');
        cy.get('#cu-privacy-notice-icon').click();

        cy.get('.panhandle-stripe.composition').should('exist');
        cy.get('.panel-subcontainer-title').contains('Untitled')
            .should('exist');
        cy.contains('ul', 'Instructor One').should('exist');
        cy.get('.project-visibility-description').contains('Draft')
            .should('exist');
        cy.get('.project-visibility-link').should('exist');
        cy.get('td.panel-container.open.composition').should('exist');
        cy.get('.project-revisionbutton').should('exist');
        cy.get('.project-previewbutton').contains('Preview').should('exist');
        cy.get('.project-previewbutton').contains('Edit').should('not.exist');
        cy.get('.project-savebutton').should('exist');
        cy.get('.participant_list').contains('Authors').should('exist');

        cy.log('write title and text and save composition');
        cy.get('.panel-subcontainer-title > .form-control').clear()
            .type('Composition: Scenario 1');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');

        cy.log('Save the project');
        cy.get('div.ajaxloader').should('not.be.visible');
        cy.get('#id_publish').should('not.be.visible');
        cy.get('.btn-save-project').should('not.be.visible');
        cy.get('.project-savebutton').contains('Save').should('be.visible');
        cy.get('.project-savebutton').click();

        cy.get('#id_publish').find('li')
            .should('contain', 'Draft - only you can view')
            .should('be.visible');
        cy.get('input[name=publish]:checked').should('exist')
            .should('be.visible');
        cy.get('#id_publish').find('li')
            .should('contain', 'Whole Class - all class members can view')
            .should('be.visible');
        cy.get('#id_publish').find('li')
            .should('not.contain', 'Whole World - a public url is provided')
            .should('be.visible');
        cy.get('.btn-save-project').should('be.visible');
        cy.get('.btn-save-project').click();
        cy.get('.btn-save-project').should('not.be.visible');

        cy.get('.project-savebutton').contains('Saved').should('exist');
        cy.get('#id_publish').should('not.be.visible');
        cy.get('.btn-save-project').should('not.be.visible');

        cy.log('toggle preview mode');
        cy.get('.project-previewbutton').contains('Preview').should('exist')
        cy.get('.project-previewbutton').click();
        cy.get('.project-revisionbutton').should('exist');
        cy.contains('Edit').should('exist');
        cy.contains('Preview').should('not.exist');
        cy.get('.project-savebutton').should('contain', 'Saved');
        cy.get('.participant_list').should('not.be', 'visible');
    });

    it('should show on Home', () => {
        cy.visit('/');
        // TODO: write this test when new Assignments tab is done.
    });

});
