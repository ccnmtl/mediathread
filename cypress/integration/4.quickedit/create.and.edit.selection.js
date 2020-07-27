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
        cy.wait(500);
    });

    it('should create a project, insert and edit selection', () => {
        cy.log('should create a composition');
        //TODO: Create composition from homepage
        cy.visit('/course/1/project/create/', {
            method: 'POST',
            body: {
                project_type: 'composition'
            }
        });
        cy.wait(500);
        cy.get('#loaded').should('exist');

        cy.log('add a title and some text');
        cy.get('#cu-privacy-notice-icon').click();
        cy.get('.page-title').click().clear()
            .type('Quick Edit Composition');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');
        cy.get('.project-savebutton').click();
        cy.get('.btn-save-project').click();

        cy.log('verify asset exists');
        cy.get('div.ajaxloader').should('not.be.visible');
        cy.get('#asset-item-2').should('contain', 'Mediathread: Introduction');

        cy.log('click the +/create button next to the asset');
        cy.get('#asset-item-2').find('.create_annotation_icon')
            .click({ force: true });

        cy.log('verify the create form is visible');
        cy.get('#annotation-current').should('exist');
        cy.contains('Title').should('exist');
        cy.contains('Tag').should('exist');
        cy.contains('Notes').should('exist');
        cy.get('[name="Cancel"]').should('exist');
        cy.get('[name="Save"]').should('exist');
        cy.get('#id_annotation-title').type('Test Selection');
        cy.get('#edit-annotation-form #s2id_id_annotation-tags .select2-input')
            .type('abc{enter}');
        cy.get('#annotation-body > #id_annotation-body')
            .type('Here are my new notes');
        cy.get('#annotation-body input[name="Save"]').click({ force: true });
        cy.get('#annotation-current').should('not.be.visible');

        cy.log('verify new selection is visible');
        cy.get('div.ajaxloader').should('not.be.visible');
        cy.get('button.btn-link').contains('Test Selection').first().click();
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
    });
});
