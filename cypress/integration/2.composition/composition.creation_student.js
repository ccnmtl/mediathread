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

        cy.visit('/course/1/project/create/', {
            method: 'POST',
            body: {
                project_type: 'composition'
            }
        });

        cy.wait(500);

        cy.get('#loaded').should('exist');
        cy.get('#cu-privacy-notice-icon').click();

        cy.get('.page-title-form input').should('be.visible');
        cy.get('.page-title-form input').should('have.value', 'Untitled')
        cy.contains('ul', 'Student One').should('exist');
        cy.get('.project-visibility-description')
            .contains('Draft').should('exist');
        cy.get('.project-revisionbutton').should('exist');
        cy.get('.project-editbutton.active').should('exist');
        cy.get('.project-previewbutton.active').should('not.exist');
        cy.get('.project-savebutton').should('exist');
        cy.get('.participant-edit-container').contains('Authors')
            .should('exist');
        cy.get('.participant-container').should('not.be.visible');

        cy.log('should save a composition');
        cy.get('.page-title-form input').clear()
            .type('Composition: Scenario 2');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');
        cy.get('.project-savebutton').click();
        cy.get('.btn-primary').contains('Save').click();
        cy.get('.project-savebutton').should('contain', 'Saved');

        cy.log('should toggle preview mode');
        cy.get('.project-previewbutton').click();
        cy.get('.project-revisionbutton').should('exist');
        cy.get('.project-editbutton.active').should('not.exist');
        cy.get('.project-previewbutton.active').should('exist');
        cy.get('.project-savebutton').should('contain', 'Saved');
        cy.get('.participant-edit-container').should('not.be', 'visible');
        cy.get('.participant-container').should('be', 'visible');
    });
    // it('should show on Home', () => {
        // TODO: adapt these for new homepage

        // cy.visit('/');
        // cy.get('#course_title_link').should('exist').click();
        // cy.get('#loaded').should('exist');
        // cy.get('li.projectlist').its('length').should('be.gt', 0);
        // cy.get('.asset_title').should('contain', 'Composition: Scenario 2');
        // cy.get('.metadata-value-author').should('contain', 'Student One');
    // });
});
