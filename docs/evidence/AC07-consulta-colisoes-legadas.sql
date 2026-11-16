-- PostgreSQL 17. Run against the legacy snapshot before applying revision 0016.
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY;
SET LOCAL statement_timeout = '30s';

WITH raw AS (
    SELECT envelope->>'environment_id' AS environment_id,
           envelope->>'account_id' AS account_id,
           envelope->>'aggregate_type' AS aggregate_type,
           envelope->>'aggregate_id' AS aggregate_id,
           envelope->>'aggregate_version' AS version_text
    FROM trade_system.outbox
), keyed AS (
    SELECT *,
           CASE WHEN pg_input_is_valid(version_text, 'numeric')
                THEN version_text::numeric END AS aggregate_version
    FROM raw
), collisions AS (
    SELECT count(*) AS affected_rows
    FROM keyed
    WHERE aggregate_version IS NOT NULL OR version_text IS NULL
    GROUP BY environment_id, account_id, aggregate_type, aggregate_id, aggregate_version
    HAVING count(*) > 1
)
SELECT (SELECT count(*) FROM raw) AS rows_examined,
       (SELECT count(*) FROM keyed
        WHERE version_text IS NOT NULL AND aggregate_version IS NULL)
           AS invalid_version_casts,
       (SELECT count(*) FROM collisions) AS collision_groups,
       (SELECT coalesce(sum(affected_rows), 0) FROM collisions) AS rows_in_collisions;

ROLLBACK;
