describe('Gestion des erreurs', () => {
    beforeEach(() => {
        cy.visit('/', {
            timeout: 30000,
            failOnStatusCode: false
        })
    })

    it('devrait gérer les erreurs d\'API', () => {
        cy.intercept('POST', '**/graphql', {
            statusCode: 500,
            body: { errors: [{ message: 'Erreur serveur' }] }
        }).as('apiError')

        cy.selectModel('total_cases')

        cy.get('body').should('be.visible')
    })

    it('devrait gérer les réponses API vides', () => {
        cy.intercept('POST', '**/graphql', {
            statusCode: 200,
            body: { data: { predictPandemic: null } }
        }).as('emptyResponse')

        cy.selectModel('total_cases')
        cy.wait('@emptyResponse')

        cy.get('p').contains('—').should('exist')
    })

    it('devrait gérer les données partielles', () => {
        cy.intercept('POST', '**/graphql', {
            statusCode: 200,
            body: {
                data: {
                    predictPandemic: {
                        official: {
                            total_cases: 1000
                        },
                        predictions: {}
                    }
                }
            }
        }).as('partialData')

        cy.selectModel('total_cases')
        cy.selectModel('total_deaths')
        cy.wait('@partialData')

        cy.get('div').contains('1000').should('be.visible')
        cy.get('p').contains('—').should('exist')
    })
})