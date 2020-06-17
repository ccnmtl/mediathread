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
        cy.wait();
    });

    it('should create a project as an Instructor', () => {
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
        cy.get('[name="Save"]').click({ force: true });
        cy.get('#annotation-current').should('not.be', 'visible');
        cy.contains('Test Selection').should('have.attr', 'href');
        cy.contains('Here are my new notes').should('exist');
        cy.get('[href="abc"]').should('exist');
    });
});
