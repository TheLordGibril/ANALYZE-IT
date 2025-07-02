import { PrismaClient } from '@prisma/client'
import fs from 'fs'
import csv from 'csv-parser'

const prisma = new PrismaClient()

async function importPays() {
  const paysSet = new Set()

  return new Promise((resolve, reject) => {
    fs.createReadStream('../../etl/datasets/full_grouped.csv')
      .pipe(csv())
      .on('data', (row) => {
        if (row['Country/Region']) paysSet.add(row['Country/Region'].trim())
      })
      .on('end', async () => {
        try {
          for (const nomPays of paysSet) {
            // Vérifie si le pays existe déjà (optionnel)
            const exist = await prisma.pays.findUnique({ where: { nom_pays: nomPays } })
            if (!exist) {
              await prisma.pays.create({ data: { nom_pays: nomPays } })
            }
          }
          console.log(`Import pays terminé, ${paysSet.size} pays traités`)
          resolve()
        } catch (e) {
          reject(e)
        }
      })
      .on('error', reject)
  })
}

async function main() {
  try {
    await importPays()
  } catch (e) {
    console.error('Erreur import pays:', e)
  } finally {
    await prisma.$disconnect()
  }
}

main()
