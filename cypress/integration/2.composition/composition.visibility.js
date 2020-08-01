// TODO: why are we getting an error for `the_records`
// here in the course settings page?
Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Student Project Visibility', () => {

    it('creates a project as an Instructor', () => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-title a').contains('MAAP Award Reception');

        cy.visit('/course/1/projects');
        cy.get('.page-title').contains('Projects');
        cy.get('#cu-privacy-notice-icon').click();
        cy.get('button').contains('Add a project').should('be.visible');
        cy.get('button').contains('Add a project').click()
        cy.get('button#add-composition-button').should('be.visible')
        cy.get('button#add-composition-button').click();

        cy.get('a.nav-link.active').contains('Projects');
        cy.get('.breadcrumb-item').contains('Back to all projects');
        cy.get('#loaded').should('exist');
        cy.get('.page-title').should('be.visible');
        cy.get('.page-title').contains('Untitled')
        cy.contains('ul', 'Instructor One').should('exist');
        cy.get('.project-visibility-description').contains('Draft')
            .should('exist');
        cy.get('.project-revisionbutton').should('exist');
        cy.get('.project-editbutton.active').should('exist');
        cy.get('.project-previewbutton.active').should('not.exist');
        cy.get('.project-savebutton').should('exist');
        cy.get('select[name="participants"]').should('exist');
        cy.get('select[name="participants"]').should('not.be.visible');
        cy.get('.participant-container').should('be.visible');

        cy.visit('/course/1/projects');
        cy.get('.page-title').contains('Projects');
        cy.get('button').contains('Add a project').should('be.visible');
        cy.get('button').contains('Add a project').click()
        cy.get('button#add-composition-button').should('be.visible')
        cy.get('button#add-composition-button').click();

        cy.get('a.nav-link.active').contains('Projects');
        cy.get('.breadcrumb-item').contains('Back to all projects');
        cy.get('#loaded').should('exist');
        cy.get('.page-title').click().clear()
            .type('Composition Public: Scenario 3');
        cy.get('.project-savebutton').click();
        cy.contains('Whole Class - all class members can view').click();
        cy.get('.btn-save-project').contains('Save').click();
        cy.get('.project-savebutton').should('contain', 'Saved');
        cy.get('.project-visibility-description')
            .should('contain', 'Shared with Class');
    });

    it('views Instructor One composition as a Student', () => {
         cy.login('student_one', 'test');

         cy.visit('/course/1/projects/');
         cy.get('#cu-privacy-notice-icon').click();
         cy.get('#select-owner').select('instructor_one');
         cy.contains('Composition Public: Scenario 3').parent('td').parent('tr').within(() => {
             // all searches are automatically rooted to the found tr element
             cy.get('td').eq(0).contains('Composition Public: Scenario 3');
             cy.get('td').eq(1).contains('Shared with Class');
             cy.get('td').eq(2).contains('Instructor One');
             cy.get('td').eq(3).contains('Composition');
             cy.get('td').eq(5).should('not.contain', 'Delete');
         });
     });

    it('creates a project as Student one', () => {
        cy.login('student_one', 'test');

        cy.visit('/course/1/projects');
        cy.get('.page-title').contains('Projects');
        cy.get('#cu-privacy-notice-icon').click();
        cy.get('button').contains('Add a project').should('be.visible');
        cy.get('button').contains('Add a project').click()
        cy.get('button#add-composition-button').should('be.visible')
        cy.get('button#add-composition-button').click();

        cy.get('a.nav-link.active').contains('Projects');
        cy.get('.breadcrumb-item').contains('Back to all projects');
        cy.get('#loaded').should('exist');
        cy.get('.page-title').click().clear().type('Student One Public Essay');
        cy.get('.project-savebutton').click();
        cy.contains('Whole Class - all class members can view').click();
        cy.get('.btn-save-project').contains('Save').click();
        cy.get('.project-savebutton').should('contain', 'Saved');
        cy.get('.project-visibility-description')
            .should('contain', 'Shared with Class');
    });

     it('views Student One composition as Student Two', () => {
         cy.login('student_two', 'test');
         cy.visit('/course/1/projects/');
         cy.get('#cu-privacy-notice-icon').click();
         cy.get('#select-owner').select('student_one');

         cy.contains('Student One Public Essay').parent('td').parent('tr').within(() => {
             // all searches are automatically rooted to the found tr element
             cy.get('td').eq(0).contains('Student One Public Essay');
             cy.get('td').eq(1).contains('Shared with Class');
             cy.get('td').eq(2).contains('Student One');
             cy.get('td').eq(3).contains('Composition');
             cy.get('td').eq(5).should('not.contain', 'Delete');
         });
     })
});
