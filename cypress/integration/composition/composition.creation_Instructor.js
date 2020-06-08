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
      cy.visit('/course/1/', { timeout: 80000 });
    });

    it('should check composition panel features', () => {
      cy.get('#homepage-create-menu').should('exist').click();
      cy.get('#create-project-menu input[type="submit"]')
        .eq(1).contains('Create Composition').click();
      cy.get('#loaded').should('exist');
      cy.get('.panhandle-stripe.composition').should('exist');
      cy.get('.panel-subcontainer-title').contains('Untitled').should('exist');
      cy.contains('ul', 'Instructor One').should('exist');
      cy.get('.project-visibility-description').contains('Draft').should('exist');
      cy.get('td.panel-container.open.composition').should('exist');
      cy.get('.project-revisionbutton').should('exist');
      cy.get('.project-previewbutton').should('exist');
      cy.contains('Edit').should('not.exist');
      cy.get('.project-savebutton').should('exist');
      cy.get('.participant_list').contains('Authors').should('exist');
    });
    it('should save a composition', () => {
      cy.visit('/project/view/1', { timeout: 80000 });
      cy.get('.panel-subcontainer-title > .form-control').clear()
        .type('Composition: Scenario 1');
      cy.getIframeBody().find('p').click()
        .type('The Columbia Center for New Teaching and Learning');
      cy.get('.project-savebutton').click();
      cy.get('#id_publish').find('li')
        .should('contain', 'Draft - only you can view')
      cy.get('input[name=publish]:checked').should('exist');
      cy.get('#id_publish').find('li')
        .should('contain', 'Whole Class - all class members can view');
      cy.get('#id_publish').find('li')
        .should('not.contain', 'Whole World - a public url is provided');
      cy.get('.project-savebutton').contains('Save').click();
      cy.get('.project-visibility-link').should('exist');
      cy.get('.btn-primary').contains('Save').click();
      cy.get('.project-savebutton').should('contain', 'Saved');
    });
    it('should toggle the preview mode', () => {
      cy.visit('/project/view/1', { timeout: 80000 });
      cy.get('.project-previewbutton').trigger('mouseover').click();
      cy.get('.project-revisionbutton').should('exist');
      cy.contains('Edit').should('exist');
      cy.contains('Preview').should('not.exist');
      cy.get('.project-savebutton').should('contain', 'Saved');
      cy.get('.participant_list').should('not.be', 'visable');
    });
    it('should show on Home', () => {
      cy.visit('/', { timeout: 80000 });
      cy.get('#course_title_link').should('exist').click();
      cy.get('#loaded').should('exist');
      cy.get('li.projectlist').its('length').should('be.gt', 0);
      cy.get('.asset_title').should('contain', 'Composition: Scenario 1');
      cy.get('.metadata-value-author').should('contain', 'Instructor One');
    });

});
