import { PrismaClient } from '@prisma/client'
import fs from 'fs'
import csv from 'csv-parser'

const prisma = new PrismaClient()

async function getIdPays(nom) {
  const pays = await prisma.pays.findUnique({ where: { nom_pays: nom } })
  if (!pays) throw new Error(`Pays non trouvé: ${nom}`)
  return pays.id_pays
}

async function getIdVirus(nom) {
  const virus = await prisma.virus.findUnique({ where: { nom_virus: nom } })
  if (!virus) throw new Error(`Virus non trouvé: ${nom}`)
  return virus.id_virus
}

async function getIdSaison(nom) {
  if (!nom) return null
  const saison = await prisma.saisons.findUnique({ where: { nom_saison: nom } })
  if (!saison) throw new Error(`Saison non trouvée: ${nom}`)
  return saison.id_saison
}

async function main() {
  const rows = []
  fs.createReadStream('../../etl/datasets/final_dataset.csv')
    .pipe(csv())
    .on('data', (row) => rows.push(row))
    .on('end', async () => {
      for (const row of rows) {
        try {
          const id_pays = await getIdPays(row.country)
          const id_virus = await getIdVirus(row.virus)
          const id_saison = await getIdSaison(row.season)

          await prisma.statistiquesJournalieres.create({
            data: {
              id_pays,
              id_virus,
              id_saison,
              date: new Date(row.date),
              nouveaux_cas: parseInt(row.new_cases) || 0,
              nouveaux_deces: parseInt(row.new_deaths) || 0,
              total_cas: parseInt(row.total_cases) || 0,
              total_deces: parseInt(row.total_deaths) || 0,
              croissance_cas: row.case_growth ? parseFloat(row.case_growth) : null,
              taux_mortalite: row.death_rate ? parseFloat(row.death_rate) : null,
              taux_infection: row.infection_rate ? parseFloat(row.infection_rate) : null,
              taux_mortalite_population: row.death_rate_pop ? parseFloat(row.death_rate_pop) : null,
              taux_infection_vs_global: row.infection_rate_vs_global ? parseFloat(row.infection_rate_vs_global) : null,
              taux_mortalite_pop_vs_global: row.death_rate_pop_vs_global ? parseFloat(row.death_rate_pop_vs_global) : null,
            }
          })
        } catch(e) {
          console.error('Erreur sur ligne:', row, e.message)
        }
      }
      console.log('Import terminé')
      await prisma.$disconnect()
    })
}

main()
