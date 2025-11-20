import { NextRequest, NextResponse } from 'next/server'
import { randomUUID } from 'crypto'

// In production, use a proper database
// For now, we'll use a simple in-memory store (replace with database)
const consentStore = new Map<string, any>()

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Validate required fields
    if (!body.name || !body.email || !body.company || !body.device || !body.scope) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      )
    }

    // Generate consent ID
    const consentId = randomUUID()

    // Store consent record
    const consentRecord = {
      consent_id: consentId,
      timestamp: new Date().toISOString(),
      name: body.name,
      email: body.email,
      company: body.company,
      device_id: body.device,
      scope: body.scope,
      authorized: body.authorized || false,
      ip_address: request.headers.get('x-forwarded-for') || 
                   request.headers.get('x-real-ip') || 
                   'unknown'
    }

    consentStore.set(consentId, consentRecord)

    // In production, save to database:
    // await db.consents.create(consentRecord)

    return NextResponse.json({
      consent_id: consentId,
      message: 'Consent recorded successfully'
    })
  } catch (error) {
    console.error('Error processing consent:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const consentId = searchParams.get('consent_id')

  if (!consentId) {
    return NextResponse.json(
      { error: 'consent_id parameter required' },
      { status: 400 }
    )
  }

  const consent = consentStore.get(consentId)
  if (!consent) {
    return NextResponse.json(
      { error: 'Consent not found' },
      { status: 404 }
    )
  }

  return NextResponse.json(consent)
}

