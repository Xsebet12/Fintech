-- Script Postgrest.sql
-- Ejecutar desde la raiz del proyecto con psql.
-- Ejemplo:
--   psql -h localhost -U postgres -d fintech -f "Script Postgrest.sql"
--
-- El script crea:
--   - una tabla de cuentas para que account_id tenga sentido
--   - una tabla de transacciones basada en fintech.csv
--   - una tabla de KPI para almacenar el resumen de monitoreo
--
-- Requiere que el CSV exista en la raiz del proyecto o ajustar la variable csv_path.

\set ON_ERROR_STOP on
\set csv_path 'fintech.csv'

CREATE SCHEMA IF NOT EXISTS fintech;

CREATE TABLE IF NOT EXISTS fintech.accounts (
    account_id TEXT PRIMARY KEY,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS fintech.transactions (
    transaction_id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    reporting_month TEXT NOT NULL,
    account_id TEXT NOT NULL REFERENCES fintech.accounts(account_id),
    counterparty_account TEXT NULL,
    transaction_group_id TEXT NULL,
    transaction_type TEXT NOT NULL,
    status TEXT NOT NULL,
    amount NUMERIC(18,2) NOT NULL,
    currency CHAR(3) NOT NULL,
    balance_before NUMERIC(18,2) NOT NULL,
    balance_after NUMERIC(18,2) NOT NULL,
    regulatory_code TEXT NULL,
    finalized BOOLEAN NOT NULL,
    record_hash TEXT NOT NULL UNIQUE,
    prev_record_hash TEXT NOT NULL,
    metadata TEXT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_amount_non_negative CHECK (amount >= 0),
    CONSTRAINT chk_currency_not_blank CHECK (btrim(currency) <> '')
);

CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON fintech.transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_reporting_month ON fintech.transactions(reporting_month);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON fintech.transactions(created_at);

CREATE TABLE IF NOT EXISTS fintech.kpi_fintech (
    kpi_id BIGSERIAL PRIMARY KEY,
    kpi_name TEXT NOT NULL,
    metric_group TEXT NOT NULL,
    reporting_month TEXT NULL,
    transaction_type TEXT NULL,
    valor NUMERIC(18,4) NOT NULL,
    descripcion TEXT NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS fintech.stg_transactions (
    transaction_id TEXT,
    created_at TEXT,
    reporting_month TEXT,
    account_id TEXT,
    counterparty_account TEXT,
    transaction_group_id TEXT,
    transaction_type TEXT,
    status TEXT,
    amount TEXT,
    currency TEXT,
    balance_before TEXT,
    balance_after TEXT,
    regulatory_code TEXT,
    finalized TEXT,
    record_hash TEXT,
    prev_record_hash TEXT,
    metadata TEXT,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

TRUNCATE TABLE fintech.kpi_fintech, fintech.transactions, fintech.accounts, fintech.stg_transactions RESTART IDENTITY CASCADE;

\echo 'Cargando CSV a la tabla staging...'
\copy fintech.stg_transactions (
    transaction_id,
    created_at,
    reporting_month,
    account_id,
    counterparty_account,
    transaction_group_id,
    transaction_type,
    status,
    amount,
    currency,
    balance_before,
    balance_after,
    regulatory_code,
    finalized,
    record_hash,
    prev_record_hash,
    metadata
)
FROM :'csv_path'
WITH (FORMAT csv, HEADER true, DELIMITER ',', QUOTE '"', ESCAPE '"');

\echo 'Registrando cuentas unicas...'
INSERT INTO fintech.accounts (account_id)
SELECT DISTINCT account_code
FROM (
    SELECT NULLIF(BTRIM(account_id), '') AS account_code
    FROM fintech.stg_transactions
    UNION
    SELECT NULLIF(BTRIM(counterparty_account), '') AS account_code
    FROM fintech.stg_transactions
) AS cuentas
WHERE account_code IS NOT NULL
ORDER BY account_code;

\echo 'Cargando transacciones normalizadas...'
INSERT INTO fintech.transactions (
    transaction_id,
    created_at,
    reporting_month,
    account_id,
    counterparty_account,
    transaction_group_id,
    transaction_type,
    status,
    amount,
    currency,
    balance_before,
    balance_after,
    regulatory_code,
    finalized,
    record_hash,
    prev_record_hash,
    metadata,
    ingested_at
)
SELECT
    NULLIF(BTRIM(transaction_id), '')::TEXT,
    NULLIF(BTRIM(created_at), '')::TIMESTAMPTZ,
    NULLIF(BTRIM(reporting_month), '')::TEXT,
    NULLIF(BTRIM(account_id), '')::TEXT,
    NULLIF(BTRIM(counterparty_account), '')::TEXT,
    NULLIF(BTRIM(transaction_group_id), '')::TEXT,
    NULLIF(BTRIM(transaction_type), '')::TEXT,
    NULLIF(BTRIM(status), '')::TEXT,
    NULLIF(BTRIM(amount), '')::NUMERIC(18,2),
    UPPER(NULLIF(BTRIM(currency), ''))::CHAR(3),
    NULLIF(BTRIM(balance_before), '')::NUMERIC(18,2),
    NULLIF(BTRIM(balance_after), '')::NUMERIC(18,2),
    NULLIF(BTRIM(regulatory_code), '')::TEXT,
    CASE
        WHEN LOWER(BTRIM(finalized)) IN ('true', '1', 'yes', 'y', 'si') THEN TRUE
        ELSE FALSE
    END,
    NULLIF(BTRIM(record_hash), '')::TEXT,
    NULLIF(BTRIM(prev_record_hash), '')::TEXT,
    NULLIF(BTRIM(metadata), '')::TEXT,
    COALESCE(ingested_at, now())
FROM fintech.stg_transactions
WHERE NULLIF(BTRIM(transaction_id), '') IS NOT NULL
  AND NULLIF(BTRIM(account_id), '') IS NOT NULL
  AND NULLIF(BTRIM(created_at), '') IS NOT NULL
  AND NULLIF(BTRIM(amount), '') IS NOT NULL
  AND NULLIF(BTRIM(record_hash), '') IS NOT NULL
  AND NULLIF(BTRIM(prev_record_hash), '') IS NOT NULL;

\echo 'Cargando KPI globales y mensuales...'
INSERT INTO fintech.kpi_fintech (
    kpi_name,
    metric_group,
    reporting_month,
    transaction_type,
    valor,
    descripcion
)
SELECT 'total_registros', 'global', NULL, NULL, COUNT(*)::NUMERIC(18,4), 'Registros totales procesados'
FROM fintech.transactions
UNION ALL
SELECT 'registros_con_cuenta', 'global', NULL, NULL, COUNT(*)::NUMERIC(18,4), 'Registros con account_id asociado'
FROM fintech.transactions
UNION ALL
SELECT 'registros_unicos', 'global', NULL, NULL, COUNT(DISTINCT transaction_id)::NUMERIC(18,4), 'Transacciones unicas'
FROM fintech.transactions
UNION ALL
SELECT 'monto_total', 'global', NULL, NULL, COALESCE(SUM(amount), 0)::NUMERIC(18,4), 'Monto total de transacciones'
FROM fintech.transactions
UNION ALL
SELECT 'monto_promedio', 'global', NULL, NULL, COALESCE(AVG(amount), 0)::NUMERIC(18,4), 'Monto promedio de transacciones'
FROM fintech.transactions
UNION ALL
SELECT 'saldo_promedio_final', 'global', NULL, NULL, COALESCE(AVG(balance_after), 0)::NUMERIC(18,4), 'Saldo promedio posterior'
FROM fintech.transactions
UNION ALL
SELECT 'transacciones_confirmadas', 'global', NULL, NULL, COUNT(*)::NUMERIC(18,4), 'Transacciones con status COMPLETED'
FROM fintech.transactions
WHERE UPPER(status) = 'COMPLETED'
UNION ALL
SELECT 'cuentas_unicas', 'global', NULL, NULL, COUNT(DISTINCT account_id)::NUMERIC(18,4), 'Cantidad de cuentas distintas'
FROM fintech.transactions
UNION ALL
SELECT 'meses_unicos', 'global', NULL, NULL, COUNT(DISTINCT reporting_month)::NUMERIC(18,4), 'Cantidad de meses de reporte distintos'
FROM fintech.transactions
UNION ALL
SELECT 'tasa_registros_validos', 'global', NULL, NULL,
       CASE
           WHEN COUNT(*) = 0 THEN 0
           ELSE ROUND((COUNT(*) FILTER (WHERE amount > 0)::NUMERIC / COUNT(*)::NUMERIC), 4)
       END,
       'Proporcion de registros con monto positivo'
FROM fintech.transactions;

INSERT INTO fintech.kpi_fintech (
    kpi_name,
    metric_group,
    reporting_month,
    transaction_type,
    valor,
    descripcion
)
SELECT
    'monto_total_por_mes',
    'monthly',
    reporting_month,
    transaction_type,
    COALESCE(SUM(amount), 0)::NUMERIC(18,4),
    'Monto total por mes y tipo de transaccion'
FROM fintech.transactions
GROUP BY reporting_month, transaction_type;

\echo 'Resumen final'
SELECT 'accounts' AS tabla, COUNT(*) AS registros FROM fintech.accounts
UNION ALL
SELECT 'transactions' AS tabla, COUNT(*) AS registros FROM fintech.transactions
UNION ALL
SELECT 'kpi_fintech' AS tabla, COUNT(*) AS registros FROM fintech.kpi_fintech;
