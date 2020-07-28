Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Assignment Feature: Student Response', () => {

    beforeEach(() => {
        cy.login('student_one', 'test');
        cy.visit('/project/view/1/');
        cy.wait(500);
        //TODO: Test navigation to sample project from new Assignments tab
    });

    it('creates a response as a Student', () => {
        cy.log('respond as a student');
        cy.get('#cu-privacy-notice-icon').click();
        cy.title().should('eq', 'Mediathread Sample Assignment');
        cy.get('.page-title').should('contain', 'Sample Assignment');
        cy.get('.project-revisionbutton').should('not.exist');
        cy.get('.project-editbutton.active').should('not.exist');
        cy.get('.project-previewbutton.active').should('not.exist');
        cy.get('.project-savebutton').should('not.exist');
        cy.get('.participant_list').should('not.be', 'visible');
        cy.get('.project-visibility').should('not.have.attr', 'href');
        cy.contains('Respond to Assignment').should('exist');

        cy.log('create the response');
        cy.contains('Respond to Assignment').trigger('mouseover')
            .click({ force: true });
        cy.get('.composition .project-revisionbutton').should('exist');
        cy.get('.composition .project-editbutton.active').should('exist');
        cy.get('.composition .project-previewbutton.active').should('not.exist');
        cy.get('.composition .project-savebutton').should('exist');
        cy.get('.composition .participant-edit-container')
            .should('be', 'visible');
        cy.get('.composition .participant-container')
            .should('not.be', 'visible');

        cy.log('Add a title and some text');
        cy.get('.composition .page-title').click().clear()
            .type('Sample Assignment Response');
        cy.get('.composition').getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');
        cy.get('.composition .project-savebutton').click();

        cy.log('Save as submitted to the instructor');
        cy.get('.project-savebutton').click({ force: true });
        cy.contains('Instructor - only author(s) and instructor can view')
            .click();
        cy.get('.btn-save-project').contains('Save');
        cy.get('.btn-save-project').click();
        cy.get('.project-visibility-description')
            .should('contain', 'Shared with Instructor');
    });

    it('should show on assignments page', () => {
        cy.visit('/course/1/assignments/');
        cy.get('#cu-privacy-notice-icon').click();
        cy.contains('Sample Assignment').parent('td').parent('tr').within(() => {
            // all searches are automatically rooted to the found tr element
            cy.get('td').eq(1).contains('Sample Assignment');
            cy.get('td').eq(2).contains('Shared with Instructor');
            cy.get('td').eq(3).contains('0 / 3');
            cy.get('td').eq(4).contains('View Response');
            cy.get('td').eq(5).contains('Composition Assignment');
        });
    });

});
