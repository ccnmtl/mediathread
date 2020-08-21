// TODO: why are we getting an error for `the_records`
// here in the course settings page?
Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Instructor creates a selection', () => {
    before(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');
    });

    it('should create a project, insert and edit selection', () => {
        cy.log('should create a composition');
        cy.visit('/course/1/projects');
        cy.get('.page-title').contains('Projects');
        cy.get('#cu-privacy-notice-icon').click();

        cy.get('button').contains('Add a project').should('be.visible');
        cy.get('button').contains('Add a project').click()
        cy.get('button#add-composition-button').should('be.visible')
        cy.get('button#add-composition-button').click();

        cy.log('add a title and some text');
        cy.get('a.nav-link.active').contains('Projects');
        cy.get('.breadcrumb-item').contains('Back to all projects');
        cy.get('#loaded').should('exist');
        cy.get('.page-title').click().clear()
            .type('Quick Edit Composition');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');
        cy.get('.project-savebutton').click();
        cy.get('.btn-save-project').click();

        cy.log('verify asset exists');
        cy.get('div.ajaxloader').should('not.be.visible');
        cy.get('#asset-item-1').should('contain', 'MAAP');

        cy.get('button.btn-link').contains('Our esteemed leaders')
            .should('be.visible');
        cy.get('button.btn-link').contains('Our esteemed leaders')
            .first().click();
        cy.get('.collapse.show').within(() => {
            cy.get('button.materialCitation').contains('Insert in Text');
            cy.get('.metadata-value').contains('One, Instructor');

            cy.log('edit the new selection is visible');
            cy.get('button').contains('Edit').click();
        });
        cy.get('#edit-annotation-form').should('be.visible');
        cy.get('#edit-annotation-form [name="annotation-title"]')
            .should('be.enabled');
        cy.wait(100);  // wait for the image to load
        cy.get('#edit-annotation-form [name="annotation-title"]')
            .clear().click().type('Rename Selection');
        cy.get('#edit-annotation-form input[name="Save"]')
            .click({ force: true });
        cy.get('#edit-annotation-form').should('not.be.visible');

        cy.log('verify new selection is visible');
        cy.get('div.ajaxloader').should('not.be.visible');
        cy.get('button.btn-link').contains('Rename Selection');

        cy.log('create a new selection');
        cy.log('click the +/create button next to the asset');
        cy.get('#record-2').find('.create-annotation')
            .click({ force: true });

        cy.log('verify the create form is visible');
        cy.get('#annotation-current').should('be.visible');
        cy.get('#annotation-body').should('be.visible');
        cy.get('input[name="annotation-title"]').type('Test Selection');
        cy.get('#edit-annotation-form .select2-input')
            .type('abc{enter}');
        cy.get('#edit-annotation-form textarea[name="annotation-body"]')
            .type('Here are my new notes');
        cy.get('#annotation-body input[name="Save"]').click({ force: true });
        cy.get('#annotation-current').should('not.be.visible');

        cy.log('verify new selection is visible');
        cy.get('div.ajaxloader').should('not.be.visible');
        cy.get('.quick-edit').should('not.be.visible');
        cy.get('.collection-materials').should('be.visible');
        cy.get('button.btn-link').contains('Test Selection')
            .should('be.visible');
        cy.get('button.btn-link').contains('Test Selection').first().click();
        cy.get('.collapse.show').within(() => {
            cy.get('button.materialCitation').contains('Insert in Text');
            cy.get('.metadata-value').contains('One, Instructor');

            cy.log('edit the new selection is visible');
            cy.get('button').contains('Edit').click();
        });
    });
});
