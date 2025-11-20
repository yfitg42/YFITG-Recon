import { NextRequest, NextResponse } from 'next/server'
import mqtt from 'mqtt'

let mqttClient: mqtt.MqttClient | null = null

function getMqttClient() {
  if (mqttClient && mqttClient.connected) {
    return mqttClient
  }

  const broker = process.env.MQTT_BROKER
  const port = parseInt(process.env.MQTT_PORT || '8883')
  const username = process.env.MQTT_USERNAME
  const password = process.env.MQTT_PASSWORD
  const useTLS = process.env.MQTT_USE_TLS === 'true'

  if (!broker || !username || !password) {
    throw new Error('MQTT configuration missing')
  }

  const options: mqtt.IClientOptions = {
    clientId: `portal-${Date.now()}`,
    username,
    password,
    clean: true,
  }

  if (useTLS) {
    options.protocol = 'mqtts'
    options.port = port
  } else {
    options.protocol = 'mqtt'
    options.port = port
  }

  mqttClient = mqtt.connect(`mqtt${useTLS ? 's' : ''}://${broker}:${port}`, options)

  mqttClient.on('error', (error) => {
    console.error('MQTT error:', error)
  })

  mqttClient.on('connect', () => {
    console.log('Connected to MQTT broker')
  })

  return mqttClient
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Validate required fields
    if (!body.device_id || !body.consent_id || !body.scope) {
      return NextResponse.json(
        { error: 'Missing required fields: device_id, consent_id, scope' },
        { status: 400 }
      )
    }

    const client = getMqttClient()

    // Wait for connection
    await new Promise((resolve, reject) => {
      if (client.connected) {
        resolve(undefined)
      } else {
        client.once('connect', resolve)
        client.once('error', reject)
        setTimeout(() => reject(new Error('MQTT connection timeout')), 5000)
      }
    })

    // Prepare MQTT payload
    const payload = {
      consent_id: body.consent_id,
      scope: body.scope,
      contact: body.contact || {},
      timestamp: new Date().toISOString(),
    }

    const topic = `device/${body.device_id}/start`

    // Publish message
    await new Promise<void>((resolve, reject) => {
      client.publish(topic, JSON.stringify(payload), { qos: 1 }, (error) => {
        if (error) {
          reject(error)
        } else {
          resolve()
        }
      })
    })

    return NextResponse.json({
      success: true,
      message: 'Start command published',
      topic,
    })
  } catch (error: any) {
    console.error('Error publishing MQTT message:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to publish start command' },
      { status: 500 }
    )
  }
}

