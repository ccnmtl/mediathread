describe('Assignment Feature: Instructor Creation', () => {

    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');
    });

    it('Instructor Creates Assignment', () => {
        cy.log('create assignment');
        cy.get('#cu-privacy-notice-button').click();

        cy.log('Navigate to the assignments page');
        cy.visit('/course/1/assignments/');
        cy.get('.btn-show-assignments').click();
        cy.get('#selection-assignment-card').should('be.visible');
        cy.get('#composition-assignment-card').should('be.visible');
        cy.get('#sequence-assignment-card').should('be.visible');
        cy.get('#discussion-assignment-card').should('be.visible');

        cy.log('Create a composition assignment');
        cy.get('#composition-assignment-card a')
            .contains('Add Assignment').click();

        cy.log('Go through the wizard');
        cy.title().should('eq', 'Mediathread Create Assignment');
        cy.wait(500);
        cy.get('a.nav-link.active').contains('Assignments');
        cy.get('.breadcrumb-item').contains('Back to all assignments');
        cy.get('.page-title').contains('Create Composition Assignment');
        cy.get('#page2').contains('Next');
        cy.get('#page2').click();

        cy.log('Add a title and some text');
        cy.get('[data-cy="step-title"]:visible').contains('1.');
        cy.get('input[name="title"]').should('be.visible');
        cy.get('input[name="title"]').click().clear()
            .type('Assignment: Scenario 1');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for Teaching and Learning');
        cy.get('#page3').should('be.visible').contains('Next');
        cy.get('#page3:visible').click();

        cy.log('Add a due date');
        cy.get('[data-cy="step-title"]:visible').contains('2.');
        cy.get('input[name="due_date"]').should('be.visible');
        cy.get('input[name="due_date"]:visible').click();
        cy.get('.ui-state-default.ui-state-highlight').click();
        cy.get('input[name="due_date"]:visible').invoke('val')
            .should('not.be.empty');
        cy.get('#ui-datepicker-div').should('not.be.visible');
        cy.get('#id_response_view_policy_0').should('be.visible');
        cy.get('#id_response_view_policy_0').click();
        cy.get('#page4').focus().click();

        cy.log('add publish options & save');
        cy.get('[data-cy="step-title"]:visible').contains('3.');
        cy.get('#id_publish_1').should('be.visible');
        cy.get('#id_publish_1').click();
        cy.get('#save-assignment').click();

        cy.title().should('eq', 'Mediathread Assignment: Scenario 1');
        cy.get('.btn-edit-assignment').should('exist');
        cy.get('#student-response-dropdown')
            .contains('0 of 3 Students Responded').should('be.visible');
        cy.get('#assignment-responses').should('not.exist');
        cy.get('#instructions-heading-one').contains('Instructions');
        cy.get('#instructions')
            .contains('The Columbia Center for Teaching and Learning');
        cy.get('.project-revisionbutton').should('not.exist');
        cy.contains('Respond To Assignment').should('not.exist');
        cy.get('#response').should('not.exist');
    });

    it('should show on assignments page', () => {
        cy.visit('/course/1/assignments');
        cy.get('#cu-privacy-notice-button').click();
        cy.contains('Assignment: Scenario 1').parent('td').parent('tr')
            .within(() => {
            // all searches are automatically rooted to the found tr element
                cy.get('td').eq(2).contains('Assignment: Scenario 1');
                cy.get('td').eq(1).contains('Shared with Class');
                cy.get('td').eq(3).contains('0 / 3');
                cy.get('td').eq(4).contains('Instructor One');
                cy.get('td').eq(5).contains('Composition');
                cy.get('td').eq(7).contains('Delete');
            });
    });
});
