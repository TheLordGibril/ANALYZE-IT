-- CreateTable
CREATE TABLE "Pays" (
    "id_pays" SERIAL NOT NULL,
    "nom_pays" VARCHAR(100) NOT NULL,

    CONSTRAINT "Pays_pkey" PRIMARY KEY ("id_pays")
);

-- CreateTable
CREATE TABLE "Virus" (
    "id_virus" SERIAL NOT NULL,
    "nom_virus" VARCHAR(50) NOT NULL,

    CONSTRAINT "Virus_pkey" PRIMARY KEY ("id_virus")
);

-- CreateTable
CREATE TABLE "Statistiques_Journalieres" (
    "id_stat" BIGSERIAL NOT NULL,
    "id_pays" INTEGER NOT NULL,
    "id_virus" INTEGER NOT NULL,
    "date" DATE NOT NULL,
    "nouveaux_cas" INTEGER NOT NULL DEFAULT 0,
    "nouveaux_deces" INTEGER NOT NULL DEFAULT 0,
    "total_cas" INTEGER NOT NULL DEFAULT 0,
    "total_deces" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "Statistiques_Journalieres_pkey" PRIMARY KEY ("id_stat")
);

-- CreateIndex
CREATE UNIQUE INDEX "Pays_nom_pays_key" ON "Pays"("nom_pays");

-- CreateIndex
CREATE UNIQUE INDEX "Virus_nom_virus_key" ON "Virus"("nom_virus");

-- CreateIndex
CREATE UNIQUE INDEX "Statistiques_Journalieres_id_pays_id_virus_date_key" ON "Statistiques_Journalieres"("id_pays", "id_virus", "date");

-- AddForeignKey
ALTER TABLE "Statistiques_Journalieres" ADD CONSTRAINT "Statistiques_Journalieres_id_pays_fkey" FOREIGN KEY ("id_pays") REFERENCES "Pays"("id_pays") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Statistiques_Journalieres" ADD CONSTRAINT "Statistiques_Journalieres_id_virus_fkey" FOREIGN KEY ("id_virus") REFERENCES "Virus"("id_virus") ON DELETE RESTRICT ON UPDATE CASCADE;
