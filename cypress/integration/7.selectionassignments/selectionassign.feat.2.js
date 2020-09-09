Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Selection Assignment Feat: Student Responds To Assignment', () => {

    before(() => {
        cy.login('student_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');
    });

    it('should create student response', () => {
        cy.visit('/course/1/assignments/');
        cy.get('#cu-privacy-notice-icon').click();
        cy.contains('Sample Selection Assignment').parent('tr').within(() => {
            // all searches are automatically rooted to the found tr element
            cy.get('td').eq(1).contains('Sample Selection Assignment');
            cy.get('td').eq(2).contains('No Response Yet');
            cy.get('td').eq(5).contains('Add Response');
            cy.get('td').eq(4).contains('Selection');

            cy.get('td').eq(5).contains('Add Response').click();
        });

        cy.title().should('contain', 'Sample Selection Assignment');
        cy.get('.btn-edit-assignment').should('not.exist');
        cy.get('button.btn-show-submit').should('be', 'disabled')

        cy.log('Create a selection');
        cy.get('button.create-selection').should('contain', 'Create Selection')
            .click();
        cy.get('#edit-annotation-form').should('be.visible');
        cy.get('[name="Save"]').should('exist');
        cy.get('[name="Save"]').click();
        cy.get('#dialog-confirm')
            .should('contain', 'Please specify a selection title');
        cy.get('.ui-dialog-buttonset > .ui-button')
            .contains('OK').click();
        cy.get('input[name="annotation-title"]').type('Foo');
        cy.get('[name="Save"]').click();
        cy.get('#edit-annotation-form').should('not.be.visible');

        cy.log('Review the selection');
        cy.get('.btn-show-submit')
            .contains('Submit 1 Selection').should('not.be', 'disabled');
        cy.get('.annotation-group .group-header .group-title')
            .contains('One, Student');
        cy.get('.annotation-group button.delete').should('be.visible');
        cy.get('.annotation-group button.edit').should('be.visible');

        cy.log('Submit the response');
        cy.get('button.btn-show-submit').click();
        cy.get('#submit-project').should('be.visible');
        cy.get('#submit-project').within(() => {
            cy.get('h4.modal-title').contains('1 Selection');
            cy.get('.submit-response').should('be.visible');
            cy.get('.submit-response').click();
        });
        cy.get('[data-cy="response-submitted-status"]')
            .contains('Submitted').should('exist');
        cy.get('[data-cy="response-submitted-status"]')
            .contains('1 Selection').should('exist');
        cy.get('.btn-show-submit').should('not.exist');
    });
});
