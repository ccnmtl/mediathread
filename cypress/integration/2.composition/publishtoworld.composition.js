describe('Publish To World Public Composition', () => {
    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
    });

    it('enables publish to world in the course & creates project', () => {
        cy.log('enable publish to world');
        cy.visit('/course/1/dashboard/settings/');
        cy.get('#cu-privacy-notice-button').click();
        if (cy.get('input#id_publish_to_world').should('not.be.checked')) {
            cy.get('input#id_publish_to_world').click();
        }
        cy.get('.btn-primary').contains('Save').click();
        cy.get('input#id_publish_to_world').should('be.checked');

        cy.log('create a project from the home page');
        cy.visit('/course/1/projects');
        cy.get('.page-title').contains('Projects');
        cy.get('button').contains('Add a project').should('be.visible');
        cy.get('button').contains('Add a project').click();
        cy.get('button#add-composition-button').should('be.visible');
        cy.get('button#add-composition-button').click();

        cy.get('a.nav-link.active').contains('Projects');
        cy.get('.breadcrumb-item').contains('Back to all projects');
        cy.get('#loaded').should('exist');

        cy.log('add title and some text');
        cy.get('.page-title').click().clear()
            .type('Composition Public: Scenario 1A');
        cy.getIframeBody().find('p').click()
            .type('The Columbia Center for New Teaching and Learning');

        cy.log('insert an asset');
        cy.get('div.ajaxloader').should('not.be.visible');
        cy.get('#asset-item-1').should('contain', 'MAAP Award Reception');
        cy.get('button.btn-link').contains('Our esteemed leaders').click();
        cy.getIframeBody().find('p').click();
        cy.get('button.materialCitation').contains('Insert in Text').click();
        cy.getIframeBody().find('a.materialCitation.asset-image')
            .contains('Our esteemed leaders');

        cy.log('save project and set project visibility to public');
        cy.get('.project-submitbutton').click();
        cy.contains('Whole World - a public url is provided').click();
        cy.get('.btn-save-project').contains('Save').click();
        cy.get('.project-visibility-description')
            .should('contain', 'Shared with World');

        cy.log('log out and go to permalink');
        //TODO: Figure out a cleaner way to do this?
        cy.get('.last-version-public')
            .should('have.attr', 'href')
            .then((href) => {
                cy.get('.sign-out').click({force: true});
                cy.visit(href);

                cy.get('.participants_chosen')
                    .should('contain', 'Instructor One');
                cy.get('.page-title')
                    .should('contain', 'Composition Public: Scenario 1A');
                cy.get('.last-version-public').should('exist');
                cy.get('.project-revisionbutton').should('not.exist');
                cy.get('.project-editbutton.active').should('not.exist');
                cy.get('.project-previewbutton.active').should('not.exist');
                cy.get('.project-savebutton').should('not.exist');
                cy.get('.project-submitbutton').should('not.exist');
                cy.get('.participant_list').should('not.exist');
                cy.get('.materialCitation').click();

                //TODO: figure out why clicking on the asset title logs you out.
                //cy.get('.annotation-title > a').should('exist')
                //.and('contain', 'MAAP Award Reception')
            });
    });
});
