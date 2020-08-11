Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Selection Assignment Feat: Instructor Creation', () => {

    before(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');
    });

    it('Instructor Creates Assignment', () => {
        cy.log('create assignment');
        cy.visit('/course/1/project/create/sa/');
        cy.get('#cu-privacy-notice-icon').click();
        //TODO: test selection creation from homepage
        cy.title().should('eq', 'Mediathread Create Assignment');
        cy.contains('Get Started').click();
        cy.contains('Choose an item from the course collection')
            .should('exist');
        cy.contains('Next').click({force: true});
        cy.get('.help-inline').should('contain', 'An item must be selected');
        cy.get('.select-asset').select('1');
        cy.contains('Next').click({force: true});
        cy.contains('Write title').should('exist');
        cy.contains('Next').click({force: true});
        cy.contains('Title is a required field').should('exist');
        cy.contains('Instructions is a required field').should('exist');
        cy.get('input[name="title"]').type('Test Selection Assignment');
        cy.getIframeBody().find('p').click()
            .type('some instructions');
        cy.contains('Next').click({force: true});
        cy.contains('Set response due date').should('exist');
        cy.contains('Next').click({force: true});
        cy.contains('Please choose a due date').should('exist');
        cy.contains('Please choose how responses will be viewed')
            .should('exist');
        cy.get('#id_response_view_policy_0').click({force: true});
        cy.get('input[name="due_date"]').type('01/01/2030');
        cy.contains('Next').click({force: true});
        cy.contains('Publish assignment to students').should('exist');
        cy.contains('Save').click({force: true});
        cy.contains('Please select who can see your work').should('exist');
        cy.get('#id_publish_1').click({force: true});
        cy.contains('Save').click({force: true});
        cy.title().should('contain', 'Test Selection Assignment');
    });
});
