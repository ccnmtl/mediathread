describe('Assignment Feature: Student Response', () => {

    beforeEach(() => {
        cy.login('student_one', 'test');
        cy.visit('/project/view/1/');
    });

    it('creates a response as a Student', () => {
        cy.log('respond as a student');
        cy.get('#cu-privacy-notice-button').click();
        cy.title().should('eq', 'Sample Assignment | Mediathread');
        cy.get('.page-title').should('contain', 'Sample Assignment');
        cy.get('[data-cy="assignment-visibility"]').should('not.exist');
        cy.get('.project-revisionbutton').should('not.exist');
        cy.get('.project-editbutton.active').should('not.exist');
        cy.get('.project-previewbutton.active').should('not.exist');
        cy.get('.project-savebutton').should('not.exist');
        cy.get('.project-submitbutton').should('not.exist');
        cy.get('.participant_list').should('not.be', 'visible');
        cy.get('.project-visibility').should('not.exist');
        cy.get('#instructions').should('be.visible');
        cy.contains('Respond to Assignment').should('exist');

        cy.log('create the response');
        cy.contains('Respond to Assignment').trigger('mouseover')
            .click({ force: true });
        cy.get('.composition .project-revisionbutton').should('exist');
        cy.get('.composition .project-editbutton.active').should('exist');
        cy.get('.composition .project-previewbutton.active')
            .should('not.exist');
        cy.get('.composition .project-savebutton').should('exist');
        cy.get('.composition .project-submitbutton').should('exist');
        //Not really sure what this checks
        // cy.get('.composition .participant-edit-container')
        //     .should('be.visible');
        cy.get('.composition .participant-container')
            .should('be.visible');
        cy.get('#instructions').should('be.visible');

        cy.log('Add a title and some text');
        cy.get('.composition .page-title').click().clear()
            .type('Sample Assignment Response');
        cy.get('.composition').getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');

        cy.log('Save as submitted to the instructor');
        cy.get('.project-submitbutton').click({force: true});
        cy.contains('Instructor - only author(s) and instructor can view')
            .click();
        cy.get('.btn-save-project').contains('Save');
        cy.get('.btn-save-project').click();

        cy.get('[data-cy="response-visibility"]')
            .contains('Shared with Instructor').should('be.visible');
    });

    it('should show on assignments page', () => {
        cy.visit('/course/1/assignments/');
        cy.get('#cu-privacy-notice-button').click();
        cy.contains('Sample Assignment').parent('tr').within(() => {
            // all searches are automatically rooted to the found tr element
            cy.get('td').eq(2).contains('Sample Assignment');
            cy.get('td').eq(1).contains('Shared with Instructor');
            cy.get('td').eq(3).contains('View Response');
            cy.get('td').eq(4).contains('Composition');
        });
    });

});
