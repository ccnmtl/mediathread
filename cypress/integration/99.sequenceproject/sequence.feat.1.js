Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Sequence Project Feat: Student Creation', () => {

    before(() => {
        cy.login('student_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');
    });

    it('Student Creates Sequence Project', () => {
        cy.get('#cu-privacy-notice-icon').click();
        cy.get('#projects-list').click();
        cy.get('#add-sequence-button').click({force: true});
        cy.title().should('contain', 'Mediathread — Untitled');
        cy.get('.btn-edit-assignment').should('not.exist');
        cy.get('button.btn-show-submit').should('not.exist');
        cy.contains('Place secondary elements').should('be.visible');
        cy.contains('Add a primary video').should('be.visible');

        cy.log('Add primary video');
        cy.contains('Add a primary video').click({force: true});
        cy.get('.switcher_collection_chooser > .switcher-top')
            .click({force: true});
        cy.get('.choice_all_items > .switcher-choice').click({force: true});

        cy.log('create selection');
        cy.get('#create-annotation-icon').click({force: true});
        cy.get('#btnClipStart').should('be.visible');
        cy.get('#btnClipEnd').should('be.visible');
        cy.get('#clipStart').clear().type('00:00:02');
        cy.get('#clipEnd').clear().type('00:00:05');
        cy.get('#annotation-title').type('Example Selection 2');
        cy.get('.col > .btn-primary').click();
        cy.get('.selection-citation-title')
            .should('contain', 'Example Selection 2');
        cy.get('#annotation-19 > .card-header > .btn').click({force: true});
        cy.get('#title').clear({force: true})
            .type('Example project', {force: true});
        //TODO: for some reasone cy.contains('Reflection') doesn't work
        cy.get('.nav > :nth-child(2) > .nav-link').click();
        cy.getIframeBody().find('p').click({force: true})
            .type('Project reflection');
        cy.get('.btn-save').click();
        cy.get('.modal-title').should('contain', 'Save Changes');
        cy.get('#id_publish_1').click();
        cy.get('.btn-save-project').click({force: true});

    });
});
