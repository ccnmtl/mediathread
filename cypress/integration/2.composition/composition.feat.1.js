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
        cy.get('.panhandle-stripe.composition').should('exist');
        cy.get('.panel-subcontainer-title').contains('Untitled')
            .should('exist');
        cy.contains('ul', 'Instructor One').should('exist');
        cy.get('.project-visibility-description').contains('Draft')
            .should('exist');
        cy.get('td.panel-container.open.composition').should('exist');
        cy.get('.project-revisionbutton').should('exist');
        cy.get('.project-previewbutton').should('exist');
        cy.contains('Edit').should('not.exist');
        cy.get('.project-savebutton').should('exist');
        cy.get('.participant_list').contains('Authors').should('exist');

        cy.log('write title and text and save composition');
        cy.get('.panel-subcontainer-title > .form-control').clear()
            .type('Composition: Scenario 1');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');
        cy.get('.project-savebutton').click();
        cy.get('#id_publish').find('li')
            .should('contain', 'Draft - only you can view');
        cy.get('input[name=publish]:checked').should('exist');
        cy.get('#id_publish').find('li')
            .should('contain', 'Whole Class - all class members can view');
        cy.get('#id_publish').find('li')
            .should('not.contain', 'Whole World - a public url is provided');
        cy.get('.project-savebutton').contains('Save').click();
        cy.get('.project-visibility-link').should('exist');
        cy.get('.btn-save-project').click();
        cy.get('.project-savebutton').should('contain', 'Saved');

        cy.log('toggle preview mode');
        cy.get('#cu-privacy-notice-icon').click();
        cy.get('.project-previewbutton').trigger('mouseover').click();
        cy.get('.project-revisionbutton').should('exist');
        cy.contains('Edit').should('exist');
        cy.contains('Preview').should('not.exist');
        cy.get('.project-savebutton').should('contain', 'Saved');
        cy.get('.participant_list').should('not.be', 'visable');
    });

    it('should show on Home', () => {
        cy.visit('/');
        // TODO: write this test when new Assignments tab is done.
    });

});
