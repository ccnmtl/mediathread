Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Selection Assignment Feat: Instructor Creation', () => {

    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.visit('/course/1/project/create/sa/');
        //cy.visit('/course/1/');
        //cy.wait(500);
    });

    it('Instructor Creates Assignment', () => {
        cy.log('create assignment');
        cy.get('#cu-privacy-notice-icon').click();
        // cy.visit('/course/1/project/create/', {
        //     method: 'POST',
        //     body: {
        //         project_type: 'assignment'
        //     }
        // });
        //
        // cy.wait(500);

        //TODO: test selection creation from homepage

        cy.title().should('eq', 'Mediathread Create Assignment');
        cy.contains('Get Started').click();
        cy.contains('Choose an item from the course collection')
            .should('exist');
        cy.contains('Next').click({force: true});
        cy.get('.help-inline').should('contain', 'An item must be selected');
        cy.get('#record-1').should('exist');
        cy.get('#record-1').click({force: true});
        cy.wait(1000);
        cy.contains('Next').click({force: true});
        cy.contains('Write title').should('exist');
        cy.contains('Next').click({force: true});
        cy.contains('Title is a required field').should('exist');
        cy.contains('Instructions is a required field').should('exist');
        cy.get(':nth-child(2) > .form-control')
            .type('Test Selection Assignment');
        cy.getIframeBody().find('p').click()
            .type('some instructions');
        cy.contains('Next').click({force: true});
        cy.contains('Set response due date').should('exist');
        cy.contains('Next').click({force: true});
        cy.contains('Please choose a due date').should('exist');
        cy.contains('Please choose how responses will be viewed')
            .should('exist');
        cy.get('#id_response_view_policy_0').click({force: true});
        cy.get('.form-group').find('due_date').type('01/01/2030');
        cy.contains('Next').click({force: true});
        cy.contains('Publish assignment to students').should('exist');
        cy.contains('Save').click({force: true});
        cy.contains('Please select who can see your work').should('exist');
        cy.get('#id_publish_1').click({force: true});
        cy.contains('Save').click({force: true});
        cy.title().should('eq', 'Test Selection Assignment page');
    });
});
