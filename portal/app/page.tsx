'use client'

import { useState, useEffect } from 'react'
import ConsentForm from './components/ConsentForm'
import SuccessScreen from './components/SuccessScreen'

export default function Home() {
  const [submitted, setSubmitted] = useState(false)
  const [consentId, setConsentId] = useState<string | null>(null)

  // Parse query parameters for prefill
  const [prefill, setPrefill] = useState({
    name: '',
    email: '',
    company: '',
    device: '',
    cidr: '',
  })

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search)
      setPrefill({
        name: params.get('name') || '',
        email: params.get('email') || '',
        company: params.get('company') || '',
        device: params.get('device') || '',
        cidr: params.get('cidr') || '',
      })
    }
  }, [])

  const handleSubmit = async (formData: any) => {
    try {
      const response = await fetch('/api/consent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        throw new Error('Failed to submit consent')
      }

      const data = await response.json()
      setConsentId(data.consent_id)
      setSubmitted(true)

      // Trigger scan via MQTT
      await fetch('/api/publishStart', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          device_id: formData.device,
          consent_id: data.consent_id,
          scope: formData.scope,
          contact: {
            name: formData.name,
            email: formData.email,
            company: formData.company,
          },
        }),
      })
    } catch (error) {
      console.error('Error submitting consent:', error)
      alert('Failed to submit consent. Please try again.')
    }
  }

  if (submitted) {
    return <SuccessScreen consentId={consentId} />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-yfitg-primary to-yfitg-secondary">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-xl p-8">
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold text-yfitg-primary mb-2">
                YFITG Network Scout
              </h1>
              <p className="text-gray-600">
                Network Security Assessment Authorization
              </p>
            </div>
            <ConsentForm prefill={prefill} onSubmit={handleSubmit} />
          </div>
        </div>
      </div>
    </div>
  )
}

