Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Selection Assignment Feat: Student Responds To Assignment', () => {

    before(() => {
        cy.login('student_one', 'test');
        cy.visit('/course/1/');
    });

    it('should create student response', () => {

        //TODO: use the UI to navigate to the Sample Selection Assignment
        cy.visit('/project/create/', {
            method: 'POST',
            body: {
                project_type: 'composition',
                parent: '2',
                title: 'My Response'
            }
        });
        cy.get('#cu-privacy-notice-icon').click({force: true});
        cy.title().should('contain', 'Sample Selection Assignment');
        cy.contains('Create a selection').click({force: true});
        cy.get('[name="Save"]').should('exist');
        cy.get('[name="Save"]').click({force: true});
        cy.get('#dialog-confirm')
            .should('contain', 'Please specify a selection title');
        cy.get('.ui-dialog-buttonset > .ui-button').click({force: true});
        cy.get('input[name="annotation-title"]').type('Foo');
        cy.get('[name="Save"]').click({force: true});
        cy.contains('Submit Response').click({force: true});
        cy.get('.submit-response').click({force: true});
        cy.contains('Submitted').should('exist');
        cy.contains('Submit Response').should('not.exist');
    });
});
