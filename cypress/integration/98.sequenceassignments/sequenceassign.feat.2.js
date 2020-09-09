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
        cy.get('#cu-privacy-notice-icon').click();
        cy.contains('Test Sequence Assignment').parent('tr').within(() => {
            // all searches are automatically rooted to the found tr element
            cy.get('td').eq(1).contains('Test Sequence Assignment');
            cy.get('td').eq(2).contains('No Response Yet');
            cy.get('td').eq(3).contains('Add Response');
            cy.get('td').eq(4).contains('Sequence Assignment');

            cy.get('td').eq(3).contains('Add Response').click();
        });
        cy.title().should('contain', 'Test Sequence Assignment');
        cy.get('.btn-edit-assignment').should('not.exist');
        cy.contains('Place secondary elements').should('be.visible');
        cy.contains('Add a primary video').should('be.visible');

        cy.log('Add primary video');
        cy.get('button.add-spine').click({force: true});
        cy.get('.switcher_collection_chooser > .switcher-top')
            .click({force: true});
        cy.get('.choice_all_items > .switcher-choice').click({force: true});

        cy.log('create selection');
        cy.get('.create_annotation_icon').click({force: true});
        cy.get('#btnClipStart').should('be.visible');
        cy.get('#btnClipEnd').should('be.visible');
        cy.get('.col > .btn-primary').click({force: true});
        cy.contains('Please specify a selection title').should('be.visible');
        cy.contains('OK').click();
        cy.get('input[name="annotation-title"]').type('Example Selection');
        cy.get('#clipStart').clear().type('00:00:02');
        cy.get('#clipEnd').clear().type('00:00:05');
        cy.get('.col > .btn-primary').click();
        cy.get('.selection-citation-title')
            .should('contain', 'Example Selection');
        cy.contains('Edit Selection').should('exist');
        cy.get('.citationTemplate > .clickableCitation').click({force: true});

        cy.log('Add secondary elements');
        cy.wait(500);
        cy.get('.jux-media > .jux-track > :nth-child(3)').click({force: true});
        cy.get('#annotation-7 > .selection-citation > :nth-child(1) > .materialCitation')
            .click();
        cy.get('.jux-txt > .jux-track > :nth-child(3)').click({force: true});
        // cy.contains('Add text annoatation').should('exist');
        cy.get('form > .form-control').type('Example annotation');
        cy.get('.modal-body > form > .btn').click();
        cy.get('.project-title').clear().type('Example response');
        cy.get('.nav-link').should('have.attr', 'href');
        //TODO: for some reasone cy.contains('Reflection') doesn't work
        cy.get('.nav > :nth-child(2) > .nav-link').click();
        cy.getIframeBody().find('p').click()
            .type('Example reflection');
        cy.get('.btn-save').click();
        cy.get('.btn-show-submit').click({force: true});
        cy.get('.alert').should('contain', 'Important!');
        cy.get('.modal-footer > .btn-primary').click({force: true});
        cy.get('.tabs-container').should('contain', 'Submitted');
    });
});
