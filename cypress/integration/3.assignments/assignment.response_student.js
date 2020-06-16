Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Assignment Feature: Student Response', () => {

    beforeEach(() => {
        cy.login('student_one', 'test');
        cy.visit('/project/view/1');
        //TODO: Test navigation to sample project from new Assignments tab
    });

    it('creates a response as a Student', () => {
        cy.log('respond as a student');
        cy.get('#cu-privacy-notice-icon').click();
        cy.title().should('eq', 'Mediathread Sample Assignment');
        cy.get('.project-title').should('contain', 'Sample Assignment');
        cy.get('.panel-container.open.assignment').should('exist');
        cy.get('.project-revisionbutton').should('not.exist');
        cy.contains('Edit').should('not.exist');
        cy.contains('Preview').should('not.exist');
        cy.get('.project-savebutton').should('not.exist');
        cy.get('.participant_list').should('not.be', 'visible');
        cy.get('.project-visibility').should('not.have.attr', 'href');
        cy.contains('Respond to Assignment').should('exist');

        cy.log('create the response');
        cy.contains('Respond to Assignment').trigger('mouseover')
            .click({ force: true });
        cy.get('.pantab.composition').should('exist');
        cy.get('.panel-container.open.assignment').should('exist');
        cy.get('.panel-container.open.composition').should('exist');
        cy.get('.project-revisionbutton').should('exist');
        cy.contains('Edit').should('not.exist');
        cy.contains('Preview').should('exist');
        cy.get('.project-savebutton').should('exist');
        cy.get('.participant_list').should('not.be', 'visible');

        cy.log('Add a title and some text');
        cy.get('.panel-subcontainer-title input[type=text]').clear()
            .type('Sample Assignment Response');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');
        cy.get('.project-savebutton').click();

        cy.log('Save as submitted to the instructor');
        cy.get('.project-savebutton').click({ force: true });
        cy.contains('Instructor - only author(s) and instructor can view')
            .click();
        cy.get('.btn-primary').contains('Save');
        cy.get('.btn-primary').click();
        cy.get('.project-visibility-link')
            .should('contain', 'Submitted to Instructor');

        cy.log('Verify home display');
        cy.get('#course_title_link').click({ force: true });
        cy.get('#loaded').should('exist');
        cy.contains('Submitted to Instructor').should('exist');
        cy.contains('Sample Assignment Response').should('exist');
        cy.contains('by Student One').should('exist');
    });
});
