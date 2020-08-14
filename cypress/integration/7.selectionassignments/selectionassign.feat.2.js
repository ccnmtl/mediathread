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
            cy.get('td').eq(3).contains('Add Response');
            cy.get('td').eq(4).contains('Selection Assignment');

            cy.get('td').eq(3).contains('Add Response').click();
        });

        cy.title().should('contain', 'Sample Selection Assignment');
        cy.get('.btn-edit-assignment').should('not.exist');
        cy.get('button.btn-show-submit').should('be', 'disabled')
        cy.get('button.create-selection').should('contain', 'Create Selection')
            .click();
        cy.get('[name="Save"]').should('exist');
        cy.get('[name="Save"]').click({force: true});
        cy.get('#dialog-confirm')
            .should('contain', 'Please specify a selection title');
        cy.get('.ui-dialog-buttonset > .ui-button')
            .contains('OK').click({force: true});
        cy.get('input[name="annotation-title"]').type('Foo');
        cy.get('[name="Save"]').click({force: true});
        cy.contains('Submit Response').click({force: true});
        cy.get('.submit-response').click({force: true});
        cy.contains('Submitted').should('exist');
        cy.contains('Submit Response').should('not.exist');
    });
});
