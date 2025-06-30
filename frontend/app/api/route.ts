import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({ 
    message: 'API is running',
    timestamp: new Date().toISOString(),
    status: 'ok'
  })
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    return NextResponse.json({ 
      message: 'Data received',
      data: body,
      timestamp: new Date().toISOString(),
      status: 'ok'
    })
  } catch (error) {
    return NextResponse.json({ 
      message: 'Invalid JSON',
      timestamp: new Date().toISOString(),
      status: 'error'
    }, { status: 400 })
  }
} 