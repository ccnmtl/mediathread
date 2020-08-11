Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Discussion View: Create Discussion', () => {

    it('Instructor Creates Discussion', () => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');

        cy.visit('/course/1/assignments/');
        cy.get('#cu-privacy-notice-icon').click();

        cy.log('Create a discussion');
        cy.get('button').contains('Add an assignment').should('be.visible');
        cy.get('button').contains('Add an assignment').click()
        cy.get('#discussion-assignment-card').should('be.visible');
        cy.get('#discussion-assignment-card a')
            .contains('Add Assignment').click()

        cy.log('create discussion wizard');
        cy.title().should('eq', 'Mediathread Create Assignment');
        cy.wait(500);
        cy.get('a.nav-link.active').contains('Assignments');
        cy.get('.breadcrumb-item').contains('Back to all assignments');
        cy.get('.page-title').contains('Create Discussion Assignment');
        cy.get('#page2').contains('Get Started');
        cy.get('#page2').click();

        cy.log('Add a title and some text');
        cy.get('h4:visible').contains('1.');
        cy.get('input[name="title"]').should('be.visible');
        cy.get('input[name="title"]').click().clear()
            .type('Discussion: Scenario 1');
        cy.getIframeBody().find('p').click()
            .type('A suitable discussion prompt');
        cy.get('#page3').should('be.visible').contains('Next');
        cy.get('#page3:visible').click();

        cy.log('Add a due date');
        cy.get('h4:visible').contains('2.');
        cy.get('input[name="due_date"]').should('be.visible');
        cy.get('input[name="due_date"]:visible').click()
        cy.get('.ui-state-default.ui-state-highlight').click();
        cy.get('input[name="due_date"]:visible').invoke('val')
            .should('not.be.empty')
        cy.get('#ui-datepicker-div').should('not.be.visible');
        cy.get('#page4').focus().click();

        cy.log('Add publish options & save');
        cy.get('h4:visible').contains('3.');
        cy.get('#id_publish_1').should('be.visible');
        cy.get('#id_publish_1').click();
        cy.get('#save-assignment').click();

        cy.log('View discussion as an instructor');
        cy.title().should('eq', 'Mediathread Discussion: Scenario 1');
        cy.get('.btn-edit-assignment').should('exist');
        cy.get('.project-visibility-description')
            .contains('Shared with Class');
        cy.get('h5').contains('Due').should('be.visible');
        cy.get('.threadedcomments-container').should('be.visible');
        cy.get('#student-response-dropdown')
            .contains('0 of 3 students responded');

        cy.get('li.comment-thread').within(() => {
            cy.get('.threaded_comment_author').contains('Instructor One');
            cy.get('.threaded_comment_text')
                .contains('A suitable discussion prompt');
            cy.get('.edit_prompt').should('be.visible');
            cy.get('.respond_prompt').should('be.visible');
        });

        cy.visit('/course/1/assignments');
        cy.contains('Discussion: Scenario 1')
            .parent('td').parent('tr').within(() => {
            // all searches are automatically rooted to the found tr element
            cy.get('td').eq(1).contains('Discussion: Scenario 1');
            cy.get('td').eq(2).contains('Shared with Class');
            cy.get('td').eq(3).contains('0 / 3');
            cy.get('td').eq(4).contains('Instructor One');
            cy.get('td').eq(5).contains('Discussion Assignment');
            cy.get('td').eq(7).contains('Delete');
        });
    });

    it('Student responds to the Discussion', () => {
        cy.login('student_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');

        cy.visit('/course/1/assignments/');
        cy.get('#cu-privacy-notice-icon').click();
        cy.get('a').contains('Add Comments').click();

        cy.log('View discussion as a student');
        cy.title().should('eq', 'Mediathread Discussion: Scenario 1');
        cy.get('.btn-edit-assignment').should('not.exist');
        cy.get('.project-visibility-description').should('not.be.visible');
        cy.get('h5').contains('Due').should('be.visible');
        cy.get('.threadedcomments-container').should('be.visible');

        cy.get('li.comment-thread').within(() => {
            cy.get('.threaded_comment_author').contains('Instructor One');
            cy.get('.threaded_comment_text')
                .contains('A suitable discussion prompt');
            cy.get('.edit_prompt').should('not.be.visible');
            cy.get('.respond_prompt').should('be.visible');
            cy.get('.respond_prompt').click();
        });

        cy.log('Add a reply');
        cy.get('button.project.cancel').should('be.visible');
        cy.get('button#comment-form-submit').should('be.visible');
        cy.getIframeBody().find('p').click()
            .type('A pithy response');
        cy.get('button#comment-form-submit').click();

        cy.log('View the reply');
        cy.get('.new-comment').within(() => {
            cy.get('.threaded_comment_author').contains('student_one');
            cy.get('.threaded_comment_text')
                .contains('A pithy response');
            cy.get('.edit_prompt').should('be.visible');
            cy.get('.respond_prompt').should('be.visible');
        });

        cy.log('View status on the assignments page');
        cy.visit('/course/1/assignments');
        cy.contains('Discussion: Scenario 1').parent('tr').within(() => {
            cy.get('td').eq(1).contains('Discussion: Scenario 1');
            cy.get('td').eq(2).contains('Shared 1 comment');
            cy.get('td').eq(3).contains('Add Comments');
        });
    });

    it('Instructor sees the response', () => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/assignments');
        cy.contains('Discussion: Scenario 1')
            .parent('td').parent('tr').within(() => {
            cy.get('td').eq(3).contains('1 / 3');
            cy.get('td').eq(7).should('not.contain', 'Delete');
        });
        cy.get('a').contains('Discussion: Scenario 1').click();
        cy.get('#student-response-dropdown')
            .contains('1 of 3 students responded');
        cy.get('#student-response-dropdown').click()
        cy.get('a.dropdown-item')
            .contains('Student One (1 comment)').should('be.visible');
    });
});
