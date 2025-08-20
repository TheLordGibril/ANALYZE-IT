describe('Analyze-it Application', () => {
    beforeEach(() => {
        cy.mockApiCall()
        cy.visit(baseUrl, {
            timeout: 30000,
            failOnStatusCode: false
        })
    })

    describe('Interface utilisateur', () => {
        it('devrait afficher le titre de l\'application', () => {
            cy.get('div').contains('Analyze-it').should('be.visible')
        })

        it('devrait avoir tous les éléments de l\'interface', () => {
            cy.get('select[name="country"]').should('be.visible')
            cy.get('select[name="virus"]').should('be.visible')
            cy.get('input[name="date_start"]').should('be.visible')
            cy.get('input[name="date_end"]').should('be.visible')

            cy.get('h4').contains('Models').should('be.visible')
            cy.get('span').contains('Tout sélectionner').should('be.visible')
        })

        it('devrait permettre de sélectionner un pays', () => {
            cy.selectCountry('Germany')
            cy.get('select[name="country"]').should('have.value', 'Germany')
        })

        it('devrait permettre de modifier le nom du virus', () => {
            cy.get('select[name="virus"]').select('Monkeypox')
            cy.get('select[name="virus"]').should('have.value', 'Monkeypox')
        })

        it('devrait permettre de modifier les dates', () => {
            cy.get('input[name="date_start"]').clear().type('2020-01-01')
            cy.get('input[name="date_end"]').clear().type('2020-12-31')

            cy.get('input[name="date_start"]').should('have.value', '2020-01-01')
            cy.get('input[name="date_end"]').should('have.value', '2020-12-31')
        })
    })

    describe('Sélection des modèles', () => {
        it('devrait permettre de sélectionner tous les modèles', () => {
            cy.get('input[type="checkbox"]').first().check()

            cy.get('input[type="checkbox"]').should('be.checked')
        })

        it('devrait permettre de désélectionner tous les modèles', () => {
            cy.get('input[type="checkbox"]').first().check()

            cy.get('input[type="checkbox"]').first().uncheck()

            cy.get('input[type="checkbox"]').should('not.be.checked')
        })

        it('devrait permettre de sélectionner des modèles individuels', () => {
            cy.selectModel('total_cases')
            cy.selectModel('total_deaths')

            cy.get('input[type="checkbox"]').parent().contains('total_cases').parent().find('input').should('be.checked')
            cy.get('input[type="checkbox"]').parent().contains('total_deaths').parent().find('input').should('be.checked')
        })
    })

    describe('Affichage des données', () => {
        it('devrait afficher les cartes numériques quand un modèle numérique est sélectionné', () => {
            cy.selectModel('total_cases')
            cy.wait('@getPrediction')

            cy.get('#total_cases').should('be.visible')
            cy.get('#total_cases').should('contain', 'total_cases')
            cy.get('#total_cases').should('contain', '14504481')
        })

        it('devrait afficher les cartes texte quand un modèle texte est sélectionné', () => {
            cy.selectModel('peak_date')
            cy.wait('@getPrediction')

            cy.get('#peak_date').should('be.visible')
            cy.get('#peak_date').should('contain', 'peak_date')
            cy.get('#peak_date').should('contain', '2022-02-02')
        })

        it('devrait afficher les graphiques quand un modèle graphique est sélectionné', () => {
            cy.selectModel('transmission_rate')
            cy.wait('@getPrediction')

            cy.get('canvas').should('be.visible')
        })

        it('devrait afficher plusieurs types de cartes simultanément', () => {
            cy.selectModel('total_cases')
            cy.selectModel('peak_date')
            cy.selectModel('transmission_rate')
            cy.wait('@getPrediction')

            cy.get('#total_cases').should('be.visible')
            cy.get('#peak_date').should('be.visible')
            cy.get('canvas').should('be.visible')
        })
    })

    describe('Interactions complètes', () => {
        it('devrait permettre de changer de pays et voir les nouvelles données', () => {
            cy.selectModel('total_cases')
            cy.wait('@getPrediction')

            cy.selectCountry('Italy')
            cy.wait('@getPrediction')

            cy.get('#total_cases').should('be.visible')
        })
    })
})