-- Table Pays
CREATE TABLE "Pays" (
    "id_pays" SERIAL PRIMARY KEY,
    "nom_pays" VARCHAR(100) UNIQUE NOT NULL,
    "population" BIGINT
);

-- Table Virus
CREATE TABLE "Virus" (
    "id_virus" SERIAL PRIMARY KEY,
    "nom_virus" VARCHAR(50) UNIQUE NOT NULL
);

-- Table Saisons
CREATE TABLE "Saisons" (
    "id_saison" SERIAL PRIMARY KEY,
    "nom_saison" VARCHAR(20) UNIQUE NOT NULL
);

-- Table Statistiques_Journalieres
CREATE TABLE "Statistiques_Journalieres" (
    "id_stat" BIGSERIAL PRIMARY KEY,
    "id_pays" INTEGER NOT NULL,
    "id_virus" INTEGER NOT NULL,
    "id_saison" INTEGER,
    "date" DATE NOT NULL,
    "nouveaux_cas" INTEGER DEFAULT 0 NOT NULL,
    "nouveaux_deces" INTEGER DEFAULT 0 NOT NULL,
    "total_cas" INTEGER DEFAULT 0 NOT NULL,
    "total_deces" INTEGER DEFAULT 0 NOT NULL,
    "croissance_cas" DECIMAL(10,4),
    "taux_mortalite" DECIMAL(10,4),
    "taux_infection" DECIMAL(10,4),
    "taux_mortalite_population" DECIMAL(10,4),
    "taux_infection_vs_global" DECIMAL(10,4),
    "taux_mortalite_pop_vs_global" DECIMAL(10,4),
    
    -- Clés étrangères
    CONSTRAINT "fk_statistiques_pays" FOREIGN KEY ("id_pays") REFERENCES "Pays"("id_pays"),
    CONSTRAINT "fk_statistiques_virus" FOREIGN KEY ("id_virus") REFERENCES "Virus"("id_virus"),
    CONSTRAINT "fk_statistiques_saison" FOREIGN KEY ("id_saison") REFERENCES "Saisons"("id_saison"),
    
    -- Unicité
    CONSTRAINT "Statistiques_Journalieres_id_pays_id_virus_date_key" UNIQUE ("id_pays", "id_virus", "date")
);

-- Table Statistiques_Globales
CREATE TABLE "Statistiques_Globales" (
    "id_global" SERIAL PRIMARY KEY,
    "id_virus" INTEGER NOT NULL,
    "date" DATE NOT NULL,
    "taux_infection_global_moyen" DECIMAL(10,4),
    "taux_mortalite_pop_global_moyen" DECIMAL(10,4),
    "total_cas_mondial" BIGINT,
    "total_deces_mondial" BIGINT,
    
    -- Clé étrangère
    CONSTRAINT "fk_globales_virus" FOREIGN KEY ("id_virus") REFERENCES "Virus"("id_virus"),
    
    -- Unicité
    CONSTRAINT "Statistiques_Globales_id_virus_date_key" UNIQUE ("id_virus", "date")
);

-- Index
CREATE INDEX "idx_statistiques_date" ON "Statistiques_Journalieres"("date");
CREATE INDEX "idx_statistiques_pays" ON "Statistiques_Journalieres"("id_pays");
CREATE INDEX "idx_statistiques_virus" ON "Statistiques_Journalieres"("id_virus");
CREATE INDEX "idx_globales_date" ON "Statistiques_Globales"("date");
CREATE INDEX "idx_globales_virus" ON "Statistiques_Globales"("id_virus");