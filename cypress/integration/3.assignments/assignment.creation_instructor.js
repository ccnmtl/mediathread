Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Assignment Feature: Instructor Creation', () => {

    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.wait(500);
    });

    it('Instructor Creates Assignment', () => {
        cy.log('create assignment');
        cy.get('#cu-privacy-notice-icon').click();
        cy.visit('/course/1/project/create/', {
            method: 'POST',
            body: {
                project_type: 'assignment'
            }
        });

        cy.wait(500);

        //cy.get('#loaded').should('exist'); Change in code?
        cy.title().should('eq', 'Mediathread Untitled');
        cy.get('.project-savebutton').should('exist');
        cy.get('.project-visibility-description').contains('Draft');

        cy.log('Add a title and some text');
        cy.get('.page-title').click().clear()
            .type('Mediathread Assignment: Scenario 1');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');
        cy.get('.project-savebutton').click();

        cy.log('Save as an Assignment');
        cy.contains('Whole Class - all class members can view').click();
        cy.get('.btn-save-project').contains('Save');
        cy.get('.btn-save-project').click();
        cy.get('.project-visibility-description')
            .should('contain', 'Shared with Class');
        cy.get('.project-savebutton').should('contain', 'Saved');

        cy.log('Toggle to preview');
        cy.get('.project-previewbutton').click();
        cy.get('.project-revisionbutton').should('exist');
        cy.get('.project-editbutton.active').should('not.exist');
        cy.get('.project-previewbutton.active').should('exist');
        cy.get('.project-savebutton').should('contain', 'Saved');
        cy.get('.participant-container').should('be', 'visible');

        //TODO: Test when the project shows up in new Assignments tab.

        cy.log('view the project in preview mode');
        cy.get('.participant-container').should('contain', 'Instructor One');
        cy.get('.project-visibility-description')
            .should('contain', 'Shared with Class');
        cy.get('.project-revisionbutton').should('exist');
        cy.get('.project-savebutton').should('contain', 'Saved');
        cy.contains('Respond To Assignment').should('not.exist');
        cy.contains('Responses (1)').should('not.exist');
    });
});
