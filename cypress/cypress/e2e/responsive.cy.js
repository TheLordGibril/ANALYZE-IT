describe('Tests responsive', () => {
    beforeEach(() => {
        cy.mockApiCall()
        cy.visit('/', {
            timeout: 30000,
            failOnStatusCode: false
        })
    })

    const viewports = [
        { width: 1920, height: 1080, name: 'Desktop Large' },
        { width: 1366, height: 768, name: 'Desktop' },
        { width: 1024, height: 768, name: 'Tablet Landscape' },
        { width: 768, height: 1024, name: 'Tablet Portrait' },
        { width: 414, height: 896, name: 'Mobile Large' },
        { width: 375, height: 667, name: 'Mobile' }
    ]

    viewports.forEach(viewport => {
        it(`devrait s'afficher correctement sur ${viewport.name} (${viewport.width}x${viewport.height})`, () => {
            cy.viewport(viewport.width, viewport.height)

            cy.get('div').contains('Analyze-it').should('be.visible')
            cy.get('select[name="country"]').should('be.visible')
            cy.get('select[name="virus"]').should('be.visible')

            cy.get('h4').contains('Models').should('be.visible')

            cy.selectModel('total_cases')
            cy.wait('@getPrediction')

            cy.get('div').contains('total_cases').should('be.visible')
        })
    })

    it('devrait gérer le défilement sur mobile', () => {
        cy.viewport(375, 667)

        cy.selectModel('total_cases')
        cy.selectModel('total_deaths')
        cy.selectModel('transmission_rate')
        cy.selectModel('peak_date')

        cy.wait('@getPrediction')

        cy.get('div').contains('total_cases').should('be.visible')
        cy.scrollTo('bottom')
        cy.get('canvas').should('be.visible')
    })

    it('devrait maintenir la fonctionnalité sur tablette', () => {
        cy.viewport(768, 1024)

        cy.selectCountry('Germany')
        cy.selectVirus('Monkeypox')
        cy.selectModel('total_cases')
        cy.selectModel('transmission_rate')

        cy.wait('@getPrediction')

        cy.get('div').contains('total_cases').should('be.visible')
        cy.get('canvas').should('be.visible')
    })

    it('devrait gérer l\'orientation mobile', () => {
        cy.viewport(414, 896)
        cy.get('div').contains('Analyze-it').should('be.visible')

        cy.viewport(896, 414)
        cy.get('div').contains('Analyze-it').should('be.visible')

        cy.get('select[name="country"]').should('be.visible')
        cy.get('select[name="virus"]').should('be.visible')
    })
})