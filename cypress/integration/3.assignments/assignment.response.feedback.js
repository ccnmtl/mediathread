Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Assignment Feature: Instructor Response Feedback', () => {

    before(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
    });

    it('Instructor provides response feedback', () => {
        cy.log('see Student response');
        cy.get('#cu-privacy-notice-icon').click();
        cy.get('.switcher_collection_chooser').should('exist');
        cy.get('.switcher-top').click();
        cy.get('.switcher-choice.owner').contains('One, Student').click();
        cy.get('.asset_title').should('contain', 'Sample Assignment');
        cy.get('.metadata-value-response')
            .should('contain', 'Sample Assignment Response');
        cy.contains('Sample Assignment Response').click();
        cy.get('#loaded').should('exist');
        cy.title().should('eq', 'Mediathread Sample Assignment Response');
        cy.get('.panhandle-stripe')
            .should('contain', 'Composition Assignment Response');
        cy.get('.panel-container.closed.assignment').should('exist');
        cy.get('.panel-container.open.composition').should('exist');
        cy.get('.project-revisionbutton').should('not.be.visible');
        cy.contains('Edit').should('not.be.visible');
        cy.get('.project-savebutton').should('not.be.visible');
        cy.contains('Create Instructor Feedback').should('exist');
        cy.get('.project-visibility').find('Submitted to Instructor')
            .should('not.have.attr', 'href');
        cy.get('.panel-container.open.discussion').should('not.exist');
        cy.get('.panel-container.closed.discussion').should('not.exist');

        cy.log('create Instructor Feedback');
        cy.get('.project-create-instructor-feedback').click();
        cy.get('.panel-container.open.discussion').should('exist');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');
        cy.get('#comment-form-submit').click();
        cy.get('.threaded_comment_author').should('contain', 'Instructor One');
    });

    it('should view Instructor feedback as Student One', () => {
        cy.login('student_one', 'test');
        cy.contains('Read Instructor Feedback').should('have.attr', 'href');
        cy.contains('Read Instructor Feedback').click();
        cy.get('#loaded').should('exist');
        cy.title().should('eq', 'Mediathread Sample Assignment Response');
        cy.get('.panel-container.open.discussion').should('exist');
        cy.get('.threaded_comment_author').should('eq', 'Instructor One');
    });
});
