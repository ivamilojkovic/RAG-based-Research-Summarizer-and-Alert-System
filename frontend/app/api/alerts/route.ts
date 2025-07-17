import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  try {
    const { query, period } = await req.json();

    const alertRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/create-alert`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, period }),
    });

    if (!alertRes.ok) {
      const errorBody = await alertRes.text();
      console.error('Backend error:', alertRes.status, errorBody);
      return new NextResponse('Failed to create alert', { status: 500 });
    }

    const alert = await alertRes.json();
    return NextResponse.json(alert);
  } catch (err) {
    console.error('Handler error:', err);
    return new NextResponse('Internal server error', { status: 500 });
  }
}

export async function GET() {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/get-alerts`);

    if (!res.ok) {
      const errorBody = await res.text();
      console.error('Backend fetch error:', res.status, errorBody);
      return new NextResponse('Failed to fetch alerts', { status: 500 });
    }

    const alerts = await res.json(); 
    return NextResponse.json(alerts);
  } catch (err) {
    console.error('GET handler error:', err);
    return new NextResponse('Internal server error', { status: 500 });
  }
}
