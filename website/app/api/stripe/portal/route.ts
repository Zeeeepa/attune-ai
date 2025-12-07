import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';

// Lazy initialization to avoid build-time errors
let stripe: Stripe | null = null;

function getStripe(): Stripe {
  if (!stripe) {
    if (!process.env.STRIPE_SECRET_KEY) {
      throw new Error('STRIPE_SECRET_KEY is not configured');
    }
    stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
  }
  return stripe;
}

export async function POST(req: NextRequest) {
  try {
    const { customerId } = await req.json();

    if (!customerId) {
      return NextResponse.json({ error: 'Customer ID is required' }, { status: 400 });
    }

    const session = await getStripe().billingPortal.sessions.create({
      customer: customerId,
      return_url: `${process.env.NEXT_PUBLIC_SITE_URL}/account`,
    });

    return NextResponse.json({ url: session.url });
  } catch (error) {
    console.error('Stripe portal error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Portal session failed';
    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}
