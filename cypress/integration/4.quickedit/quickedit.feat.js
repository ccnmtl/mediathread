// TODO: why are we getting an error for `the_records`
// here in the course settings page?
Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Instructor Edits the Item Metadata', () => {
    before(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
    });

    it('should create a composition as an Instructor', () => {
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
        cy.get('.panel-subcontainer-title > .form-control').clear()
            .type('Quick Edit Composition');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');
        cy.get('.project-savebutton').click();
        cy.get('.btn-save-project').click();

        cy.log('verify asset exists');
        cy.get('#asset-item-2').should('contain', 'Mediathread: Introduction');
        cy.get('.annotation-global-body')
            .should('contain', 'instructor_one item note');

        cy.log('click edit item');
        cy.get('#asset-item-2 > .actions > .edit-asset > .edit_icon')
            .trigger('mouseover').click({ force: true });

        cy.log('verify the create form is visible');
        cy.get('#asset-global-annotation-quick-edit').should('exist');
        cy.get('#edit-global-annotation-form').find('textarea').clear()
            .type('Here are my notes');
        cy.get('#edit-global-annotation-form #s2id_id_annotation-tags .select2-input')
            .type('ghi{enter}');
        cy.contains('Save Item').click();
        cy.get('#asset-global-annotation-quick-edit')
            .should('not.be', 'visible');
        cy.get('.annotation-global-body')
            .should('contain', 'Here are my notes');
        cy.get('[href="ghi"]').should('exist');
    });
});
