'use server'

import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export async function getAlertById(id: string) {
  const result = await pool.query(
    `SELECT id, summary FROM alerts WHERE id = $1`,
    [id]
  );

  if (result.rows.length === 0) return null;

  const row = result.rows[0];
  console.log("Summary from DB: ", row.summary)

  try {
    // summary is stored as a JSON string
    const parsedSummary = JSON.parse(row.summary);
    return { id: row.id, summary: parsedSummary };
  } catch (err) {
    console.error('Error parsing summary JSON:', err);
    return null;
  }
}
