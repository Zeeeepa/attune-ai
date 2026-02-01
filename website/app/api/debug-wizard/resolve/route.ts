/**
 * Debug Wizard Resolve API Route
 *
 * Stores resolved bug patterns for future reference.
 * Patterns are stored in Redis for persistence across sessions.
 */

export const dynamic = 'force-dynamic';

import { NextResponse } from 'next/server';
import { storeBugPattern, type StoredBugPattern } from '@/lib/redis';

interface ResolveInput {
  bug_id: string;
  error_type: string;
  error_message: string;
  file_path: string;
  root_cause: string;
  fix_applied: string;
  fix_code?: string;
  resolution_time_minutes: number;
  user_id?: string;
}

/**
 * Get file extension from path
 */
function getFileExtension(filePath: string): string {
  const parts = filePath.split('.');
  return parts.length > 1 ? `.${parts[parts.length - 1]}` : 'unknown';
}

export async function POST(request: Request): Promise<Response> {
  try {
    const body: ResolveInput = await request.json();
    const {
      bug_id,
      error_type,
      error_message,
      file_path,
      root_cause,
      fix_applied,
      fix_code,
      resolution_time_minutes,
      user_id,
    } = body;

    // Validate required fields
    if (!bug_id || !error_type || !error_message || !root_cause || !fix_applied) {
      return NextResponse.json(
        {
          success: false,
          error: 'Missing required fields: bug_id, error_type, error_message, root_cause, fix_applied',
        },
        { status: 400 }
      );
    }

    // Create pattern to store
    const pattern: StoredBugPattern = {
      id: bug_id,
      date: new Date().toISOString().slice(0, 10),
      error_type,
      error_message,
      file_path: file_path || 'unknown',
      file_type: file_path ? getFileExtension(file_path) : 'unknown',
      root_cause,
      fix_applied,
      fix_code: fix_code || null,
      resolution_time_minutes: resolution_time_minutes || 0,
      user_id,
    };

    // Store pattern (Redis or in-memory fallback)
    const stored = await storeBugPattern(pattern);

    if (!stored) {
      return NextResponse.json(
        {
          success: false,
          error: 'Failed to store pattern',
        },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      data: {
        pattern_id: bug_id,
        stored: true,
        message: 'Bug pattern stored successfully. This will help with future debugging!',
      },
    });
  } catch (error) {
    console.error('Debug wizard resolve error:', error);

    return NextResponse.json(
      {
        success: false,
        error: 'Internal server error',
      },
      { status: 500 }
    );
  }
}
