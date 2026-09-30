-- Portable analytical sketch after loading normalized results into a database.
-- Bind :run_id through your client's parameter mechanism, never string interpolation.
SELECT provider,
       SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) AS passed,
       SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) AS failed,
       SUM(CASE WHEN status = 'UNKNOWN' THEN 1 ELSE 0 END) AS unknown,
       SUM(CASE WHEN status = 'NOT_APPLICABLE' THEN 1 ELSE 0 END) AS not_applicable
FROM control_results
WHERE run_id = :run_id
GROUP BY provider;
