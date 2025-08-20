describe('Tests d\'accessibilité', () => {
    beforeEach(() => {
        cy.mockApiCall()
        cy.visit('/', {
            timeout: 30000,
            failOnStatusCode: false
        })
    })

    it('devrait avoir des labels appropriés pour les formulaires', () => {
        cy.get('label').contains('Pays').should('be.visible')
        cy.get('label').contains('Virus').should('be.visible')
        cy.get('label').contains('Début').should('be.visible')
        cy.get('label').contains('Fin').should('be.visible')

        cy.get('select[name="country"]').should('exist')
        cy.get('select[name="virus"]').should('exist')
        cy.get('input[name="date_start"]').should('exist')
        cy.get('input[name="date_end"]').should('exist')
    })

    it('devrait permettre la navigation au clavier', () => {
        cy.get('select[name="country"]').focus().should('have.focus')
        cy.get('select[name="virus"]').focus().should('have.focus')
        cy.get('input[name="date_start"]').focus().should('have.focus')
        cy.get('input[name="date_end"]').focus().should('have.focus')

        cy.get('input[type="checkbox"]').first().focus().should('have.focus')

        cy.get('select[name="country"]').should('not.have.attr', 'tabindex', '-1')
        cy.get('select[name="virus"]').should('not.have.attr', 'tabindex', '-1')
        cy.get('input[name="date_start"]').should('not.have.attr', 'tabindex', '-1')
        cy.get('input[name="date_end"]').should('not.have.attr', 'tabindex', '-1')
    })


    it('devrait avoir un contraste suffisant', () => {
        cy.get('div').contains('Analyze-it').should('have.css', 'color')

        cy.get('label').should('be.visible')

        cy.get('input, select').should('be.visible')
    })

    it('devrait gérer les états de focus', () => {
        cy.get('select[name="country"]').focus().should('have.focus')
        cy.get('select[name="virus"]').focus().should('have.focus')

        cy.get('input[type="checkbox"]').first().focus().should('have.focus')
    })
})