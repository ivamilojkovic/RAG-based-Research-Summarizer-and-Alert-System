import { getAlertById } from '@/lib/db';
import { NextResponse } from 'next/server';

export async function GET(req: Request, { params }: { params: Promise<{ id: string }> }) {
  // Await the params Promise to get the actual parameters
  const { id } = await params;

  try {
    const alert = await getAlertById(id);

    if (!alert) {
      return NextResponse.json({ error: 'Alert not found' }, { status: 404 });
    }

    return NextResponse.json(alert);
  } catch (err) {
    console.error('Error fetching alert:', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}