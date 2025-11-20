'use client'

import { useState } from 'react'

interface ConsentFormProps {
  prefill: {
    name: string
    email: string
    company: string
    device: string
    cidr: string
  }
  onSubmit: (data: any) => void
}

export default function ConsentForm({ prefill, onSubmit }: ConsentFormProps) {
  const [formData, setFormData] = useState({
    name: prefill.name,
    email: prefill.email,
    company: prefill.company,
    device: prefill.device || '',
    scope: {
      cidr: prefill.cidr ? [prefill.cidr] : ['192.168.1.0/24'],
      http_hosts: [] as string[],
    },
    authorized: false,
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  const validate = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required'
    }

    if (!formData.email.trim() || !formData.email.includes('@')) {
      newErrors.email = 'Valid email is required'
    }

    if (!formData.company.trim()) {
      newErrors.company = 'Company name is required'
    }

    if (!formData.device.trim()) {
      newErrors.device = 'Device ID is required'
    }

    if (!formData.scope.cidr.length) {
      newErrors.cidr = 'At least one CIDR range is required'
    }

    if (!formData.authorized) {
      newErrors.authorized = 'You must authorize the scan'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (validate()) {
      onSubmit(formData)
    }
  }

  const addCidr = () => {
    setFormData({
      ...formData,
      scope: {
        ...formData.scope,
        cidr: [...formData.scope.cidr, ''],
      },
    })
  }

  const updateCidr = (index: number, value: string) => {
    const newCidr = [...formData.scope.cidr]
    newCidr[index] = value
    setFormData({
      ...formData,
      scope: {
        ...formData.scope,
        cidr: newCidr,
      },
    })
  }

  const removeCidr = (index: number) => {
    const newCidr = formData.scope.cidr.filter((_, i) => i !== index)
    setFormData({
      ...formData,
      scope: {
        ...formData.scope,
        cidr: newCidr,
      },
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
          Full Name *
        </label>
        <input
          type="text"
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-yfitg-accent focus:border-transparent ${
            errors.name ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
          Email Address *
        </label>
        <input
          type="email"
          id="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-yfitg-accent focus:border-transparent ${
            errors.email ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
      </div>

      <div>
        <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-1">
          Company Name *
        </label>
        <input
          type="text"
          id="company"
          value={formData.company}
          onChange={(e) => setFormData({ ...formData, company: e.target.value })}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-yfitg-accent focus:border-transparent ${
            errors.company ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        {errors.company && <p className="mt-1 text-sm text-red-600">{errors.company}</p>}
      </div>

      <div>
        <label htmlFor="device" className="block text-sm font-medium text-gray-700 mb-1">
          Device ID *
        </label>
        <input
          type="text"
          id="device"
          value={formData.device}
          onChange={(e) => setFormData({ ...formData, device: e.target.value })}
          placeholder="scout-001"
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-yfitg-accent focus:border-transparent ${
            errors.device ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        <p className="mt-1 text-sm text-gray-500">Found on device label or QR code</p>
        {errors.device && <p className="mt-1 text-sm text-red-600">{errors.device}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Network Scope (CIDR Ranges) *
        </label>
        {formData.scope.cidr.map((cidr, index) => (
          <div key={index} className="flex gap-2 mb-2">
            <input
              type="text"
              value={cidr}
              onChange={(e) => updateCidr(index, e.target.value)}
              placeholder="192.168.1.0/24"
              className={`flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-yfitg-accent focus:border-transparent ${
                errors.cidr ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {formData.scope.cidr.length > 1 && (
              <button
                type="button"
                onClick={() => removeCidr(index)}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
              >
                Remove
              </button>
            )}
          </div>
        ))}
        <button
          type="button"
          onClick={addCidr}
          className="mt-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
        >
          + Add CIDR Range
        </button>
        {errors.cidr && <p className="mt-1 text-sm text-red-600">{errors.cidr}</p>}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <input
            type="checkbox"
            id="authorized"
            checked={formData.authorized}
            onChange={(e) => setFormData({ ...formData, authorized: e.target.checked })}
            className="mt-1 mr-3"
          />
          <label htmlFor="authorized" className="text-sm text-gray-700">
            <strong>I authorize YFITG to perform a non-intrusive network security assessment</strong>
            <br />
            <span className="text-gray-600">
              This scan will only perform port enumeration, service detection, and configuration checks.
              No password attempts, exploitation, or network disruption will occur. Estimated duration: 1-2 hours.
            </span>
          </label>
        </div>
        {errors.authorized && (
          <p className="mt-2 text-sm text-red-600">{errors.authorized}</p>
        )}
      </div>

      <button
        type="submit"
        className="w-full bg-yfitg-accent text-white py-3 px-6 rounded-lg font-semibold hover:bg-yfitg-secondary transition-colors"
      >
        Authorize & Start Scan
      </button>
    </form>
  )
}

