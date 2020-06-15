Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Assignment Feature: Instructor Creation', () => {

    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
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
        cy.get('#loaded').should('exist');
        cy.title().should('eq', 'Mediathread Untitled');
        // cy.get('.panel-subcontainer-title').contains('Untitled');
        cy.get('.panel-container.open.assignment').should('exist');
        cy.get('.project-savebutton').should('exist');
        cy.get('.project-visibility-description').contains('Draft');

        cy.log('Add a title and some text');
        cy.get('.panel-subcontainer-title input[type=text]').clear()
            .type('Assignment: Scenario 1');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');
        cy.get('.project-savebutton').click();

        cy.log('Save as an Assignment');
        cy.contains('Whole Class - all class members can view').click();
        cy.get('.btn-primary').contains('Save');
        cy.get('.btn-primary').click();
        cy.get('.project-visibility-link')
            .should('contain', 'Published to Class');
        cy.get('.panel-container.open.assignment').should('exist');
        cy.get('.project-savebutton').should('contain', 'Saved');

        cy.log('Toggle to preview');
        cy.get('.project-previewbutton').trigger('mouseover')
            .click({ force: true });
        cy.get('.project-revisionbutton').should('exist');
        cy.contains('Edit').should('exist');
        cy.contains('Preview').should('not.exist');
        cy.get('.project-savebutton').should('contain', 'Saved');
        cy.get('.participant_list').should('not.be', 'visible');

        cy.log('project shows');
        cy.visit('/course/1/');
        cy.get('#loaded').should('exist');
        cy.get('.asset_title').should('contain', 'Assignment: Scenario 1');
        cy.get('.metadata-value-author').should('contain', 'Instructor One');

        cy.log('view the project in preview mode');
        cy.contains('Assignment: Scenario 1').click();
        cy.get('#loaded').should('exist');
        //cy.get('.project-title').should('contain', 'Assignment: Scenario 1');
        cy.title().should('eq', 'Mediathread Assignment: Scenario 1');

        cy.log('Preview view elements');
        cy.get('.participants_chosen').should('contain', 'Instructor One');
        cy.get('.project-visibility-link').should('have.attr', 'href');
        cy.get('.project-visibility-description')
            .should('contain', 'Published to Class');
        cy.get('td.panel-container.open.assignment').should('exist');
        cy.get('.project-revisionbutton').should('exist');
        cy.get('.participant_list').should('not.be', 'visible');
        cy.get('.project-savebutton').should('contain', 'Saved');
        cy.contains('Respond To Assignment').should('not.exist');
        cy.contains('Responses (1)').should('not.exist');
    });
});
