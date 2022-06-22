Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Sequence Assignment Feat: Student Responds To Assignment', () => {

    before(() => {
        cy.login('student_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');
    });

    it('should create student response', () => {
        cy.contains('Assignments').click();
        cy.get('#cu-privacy-notice-button').click();
        cy.contains('Test Sequence Assignment').parent('tr').within(() => {
            // all searches are automatically rooted to the found tr element
            cy.get('td').eq(2).contains('Test Sequence Assignment');
            cy.get('td').eq(1).contains('No Response');
            cy.get('td').eq(3).contains('Add Response');
            cy.get('td').eq(4).contains('Sequence');

            cy.get('td').eq(3).contains('Add Response').click();
        });
        cy.title().should('contain', 'Test Sequence Assignment');
        cy.get('.btn-edit-assignment').should('not.exist');
        cy.contains('Place secondary elements').should('be.visible');
        cy.contains('Add a primary video').should('be.visible');

        cy.log('Add primary video');
        cy.wait(500);
        cy.get('button.add-spine').should('be.visible');
        cy.get('button.add-spine').click({force: true});
        cy.get('.switcher_collection_chooser > .switcher-top')
            .click({force: true});
        cy.get('.choice_all_items > .switcher-choice').click({force: true});

        cy.log('create selection');
        cy.get('#create-annotation-icon').should('be.visible');
        cy.get('#create-annotation-icon').click({force: true});
        cy.get('#btnClipStart').should('be.visible');
        cy.get('#btnClipEnd').should('be.visible');
        cy.get('.col > .btn-primary').click({force: true});
        cy.contains('Please specify a selection title').should('be.visible');
        cy.contains('OK').click();
        cy.get('input[name="annotation-title"]').type('Example Selection');
        cy.get('#clipStart').clear().type('00:00:02');
        cy.get('#clipEnd').clear().type('00:00:05');
        cy.get('.col > .btn-primary[value="Save Selection"]').click();
        cy.get('div.collection-modal').should('not.exist');

        // Verify the selection was created
        cy.get('.selection-citation-title').contains('Example Selection')
            .should('be.visible');

        // Add it to the spine
        cy.get('.selection-citation-title').contains('Example Selection')
            .first().click();
        cy.get('.collapse.show').within(() => {
            cy.contains('Edit Selection').should('exist');
            cy.contains('Insert').should('exist');
            cy.get('#insert-selection').click({force: true});
        });
        cy.get('button.add-spine').should('not.exist');

        cy.log('Add secondary elements');
        cy.get('.jux-track-container.jux-txt .jux-track .jux-snap-column')
            .first().click({force: true});
        cy.get('.modal-title').contains('Add text annotation')
            .should('be.visible');
        cy.get('.modal-body > form > textarea').type('Example annotation');
        cy.get('.modal-body > form > .btn-primary').click();
        cy.get('.modal-title').contains('Add text annotation')
            .should('not.exist');

        cy.get('#response-title').clear({force: true}).type('Example response');

        // Add a reflection
        cy.get('.nav .nav-link').contains('Reflection').click();
        cy.getIframeBody().find('p').click({force: true})
            .type('Example reflection');
        cy.get('.btn-save').click();
        cy.get('.btn-show-submit').click({force: true});
        cy.get('.alert').should('contain', 'Important!');
        cy.get('.modal-footer > .btn-primary').click({force: true});
        cy.get('.tabs-container').should('contain', 'Submitted');
    });
});
