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

// Fallback site URL in case env var is not set
const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://smartaimemory.com';

export async function POST(req: NextRequest) {
  try {
    const { priceId, mode, customerEmail, successUrl, cancelUrl } = await req.json();

    if (!priceId) {
      return NextResponse.json({ error: 'Price ID is required' }, { status: 400 });
    }

    // Validate priceId is not a placeholder
    if (priceId.includes('placeholder')) {
      return NextResponse.json({ error: 'Product not configured. Please contact support.' }, { status: 400 });
    }

    const session = await getStripe().checkout.sessions.create({
      mode: mode || 'payment', // 'payment' for one-time, 'subscription' for recurring
      payment_method_types: ['card'],
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      success_url: successUrl || `${SITE_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: cancelUrl || `${SITE_URL}/pricing`,
      customer_email: customerEmail || undefined,
      allow_promotion_codes: true,
      billing_address_collection: 'required',
      // Collect customer info for fulfillment
      customer_creation: mode === 'subscription' ? undefined : 'always',
    });

    return NextResponse.json({ url: session.url, sessionId: session.id });
  } catch (error) {
    console.error('Stripe checkout error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Checkout failed';
    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}
