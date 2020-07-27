Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Assignment Feature: Instructor Creation', () => {

    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.wait(500);
    });

    it('Instructor Creates Assignment', () => {
        cy.log('create assignment');
        cy.get('#cu-privacy-notice-icon').click();

        cy.log('Navigate to the assignments page');
        cy.visit('/course/1/assignments/');
        cy.get('.btn-show-assignments').click();
        cy.get('#selection-assignment-card').should('be.visible');
        cy.get('#composition-assignment-card').should('be.visible');
        cy.get('#sequence-assignment-card').should('be.visible');
        cy.get('#discussion-assignment-card').should('be.visible');

        cy.log('Create a composition assignment');
        cy.get('#composition-assignment-card a')
            .contains('Add Assignment').click()

        cy.log('Go through the wizard');
        cy.title().should('eq', 'Mediathread Create Assignment');
        cy.wait(500);
        cy.get('a.nav-link.active').contains('Assignments');
        cy.get('.breadcrumb-item').contains('Back to assignments');
        cy.get('.page-title').contains('Create Composition Assignment');
        cy.get('#page2').contains('Get Started');
        cy.get('#page2').click({'force': true});

        cy.log('Add a title and some text');
        cy.get('input[name="title"]').click().clear()
            .type('Assignment: Scenario 1');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for Teaching and Learning');
        cy.get('#page3').click();

        cy.log('Add a due date');
        cy.get('input[name="due_date"]').click()
        cy.get('.ui-state-default.ui-state-highlight').click();
        cy.get('input[name="due_date"]').invoke('val').should('not.be.empty')
        cy.get('#page4').focus().click();

        cy.log('add publish options & save');
        cy.get('#id_publish_1').should('be.visible');
        cy.get('#id_publish_1').click();
        cy.get('#save-assignment').click();

        //cy.get('#loaded').should('exist'); Change in code?
        cy.title().should('eq', 'Mediathread Assignment: Scenario 1');
        cy.get('.btn-edit-assignment').should('exist');
        cy.get('.project-visibility-description').contains('Shared with Class');
        cy.get('#assignment-responses').should('not.be.visible');
        cy.get('#instructions-heading-one').contains('Instructions');
        cy.get('#instructions')
            .contains('The Columbia Center for Teaching and Learning');
        cy.get('.project-revisionbutton').should('not.be.visible');
        cy.contains('Respond To Assignment').should('not.exist');

        it('should show on projects page', () => {
            cy.visit('/course/1/assignments');
            cy.contains('Assignment: Scenario 1').parent('td').parent('tr').within(() => {
                // all searches are automatically rooted to the found tr element
                cy.get('td').eq(1).contains('Assignment: Scenario 1');
                cy.get('td').eq(2).contains('Shared with Class');
                cy.get('td').eq(3).contains('0 / 3');
                cy.get('td').eq(4).contains('Instructor One');
                cy.get('td').eq(5).contains('Composition Assignment');
                cy.get('td').eq(7).contains('Delete');
            });
        });


        //TODO: Test when the project shows up in new Assignments tab.

    });
});
