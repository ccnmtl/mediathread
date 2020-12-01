Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Sequence Assignment Feat: Instructor Creation', () => {

    before(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');
    });

    it('Instructor Creates Sequence Assignment', () => {
        cy.log('create assignment');
        cy.visit('/course/1/assignments/');
        cy.get('#cu-privacy-notice-button').click();
        cy.contains('Add an assignment').click({force: true});
        cy.get('#addSequenceAssignment').click({force: true});
        cy.contains('Next').click();
        cy.title().should('eq', 'Mediathread Create Sequence Assignment');
        cy.contains('Next').click({force: true});
        cy.contains('Write title & instructions').should('exist');
        cy.contains('Next').click({force: true});
        cy.contains('Title is a required field').should('exist');
        cy.contains('Instructions is a required field').should('exist');
        cy.get('input[name="title"]').type('Test Sequence Assignment');
        cy.getIframeBody().find('p').click()
            .type('Example instructions');
        cy.contains('Next').click({force: true});
        cy.get('textarea[name="custom_instructions_1"]').type('test');
        cy.get('#summary_ifr').type('Example summary');
        cy.contains('Set response due date & visibility').should('exist');
        cy.contains('Next').click({force: true});
        cy.contains('Please choose a due date').should('exist');
        cy.contains('Please choose how responses will be viewed')
            .should('exist');
        cy.get('#id_response_view_policy_2').click({force: true});
        cy.get('input[name="due_date"]').type('01/01/2030');
        cy.contains('Next').click({force: true});
        cy.contains('Publish assignment to students').should('exist');
        cy.contains('Save').click({force: true});
        cy.contains('Please select who can see your work').should('exist');
        cy.get('#id_publish_1').click({force: true});
        cy.contains('Save').click({force: true});
        cy.title().should('contain', 'Test Sequence Assignment');
    });
});
