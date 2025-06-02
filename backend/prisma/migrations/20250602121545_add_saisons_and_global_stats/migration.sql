-- AlterTable
ALTER TABLE "Pays" ADD COLUMN     "population" BIGINT;

-- AlterTable
ALTER TABLE "Statistiques_Journalieres" ADD COLUMN     "croissance_cas" DECIMAL(10,4),
ADD COLUMN     "id_saison" INTEGER,
ADD COLUMN     "taux_infection" DECIMAL(10,4),
ADD COLUMN     "taux_infection_vs_global" DECIMAL(10,4),
ADD COLUMN     "taux_mortalite" DECIMAL(10,4),
ADD COLUMN     "taux_mortalite_pop_vs_global" DECIMAL(10,4),
ADD COLUMN     "taux_mortalite_population" DECIMAL(10,4);

-- CreateTable
CREATE TABLE "Saisons" (
    "id_saison" SERIAL NOT NULL,
    "nom_saison" VARCHAR(20) NOT NULL,

    CONSTRAINT "Saisons_pkey" PRIMARY KEY ("id_saison")
);

-- CreateTable
CREATE TABLE "Statistiques_Globales" (
    "id_global" SERIAL NOT NULL,
    "id_virus" INTEGER NOT NULL,
    "date" DATE NOT NULL,
    "taux_infection_global_moyen" DECIMAL(10,4),
    "taux_mortalite_pop_global_moyen" DECIMAL(10,4),
    "total_cas_mondial" BIGINT,
    "total_deces_mondial" BIGINT,

    CONSTRAINT "Statistiques_Globales_pkey" PRIMARY KEY ("id_global")
);

-- CreateIndex
CREATE UNIQUE INDEX "Saisons_nom_saison_key" ON "Saisons"("nom_saison");

-- CreateIndex
CREATE UNIQUE INDEX "Statistiques_Globales_id_virus_date_key" ON "Statistiques_Globales"("id_virus", "date");

-- AddForeignKey
ALTER TABLE "Statistiques_Journalieres" ADD CONSTRAINT "Statistiques_Journalieres_id_saison_fkey" FOREIGN KEY ("id_saison") REFERENCES "Saisons"("id_saison") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Statistiques_Globales" ADD CONSTRAINT "Statistiques_Globales_id_virus_fkey" FOREIGN KEY ("id_virus") REFERENCES "Virus"("id_virus") ON DELETE RESTRICT ON UPDATE CASCADE;
