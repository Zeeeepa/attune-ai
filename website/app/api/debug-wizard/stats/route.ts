/**
 * Debug Wizard Stats API Route
 *
 * Returns statistics about stored bug patterns.
 */

export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import { getPatternStats, isRedisAvailable } from '@/lib/redis';

export async function GET(): Promise<Response> {
  try {
    const stats = await getPatternStats();

    return NextResponse.json({
      success: true,
      data: {
        total_patterns: stats.total,
        patterns_by_type: stats.byType,
        storage_mode: stats.mode,
        redis_available: isRedisAvailable(),
        environment: stats.environment,
        key_prefix: stats.keyPrefix,
      },
    });
  } catch (error) {
    console.error('Debug wizard stats error:', error);

    return NextResponse.json(
      {
        success: false,
        error: 'Failed to retrieve stats',
      },
      { status: 500 }
    );
  }
}
