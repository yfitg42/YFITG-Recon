'use client'

interface SuccessScreenProps {
  consentId: string | null
}

export default function SuccessScreen({ consentId }: SuccessScreenProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-yfitg-primary to-yfitg-secondary flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full text-center">
        <div className="mb-6">
          <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
            <svg
              className="w-8 h-8 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-yfitg-primary mb-2">
            Scan Started Successfully
          </h2>
          <p className="text-gray-600 mb-4">
            Your network security assessment has been authorized and started.
          </p>
        </div>

        {consentId && (
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-gray-600 mb-1">Consent ID</p>
            <p className="font-mono text-sm text-gray-800">{consentId}</p>
          </div>
        )}

        <div className="space-y-4 text-left">
          <div className="flex items-start">
            <div className="flex-shrink-0 w-6 h-6 bg-yfitg-accent text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
              1
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">Scan in Progress</h3>
              <p className="text-sm text-gray-600">
                The device is now scanning your network using safe, non-intrusive techniques.
              </p>
            </div>
          </div>

          <div className="flex items-start">
            <div className="flex-shrink-0 w-6 h-6 bg-yfitg-accent text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
              2
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">Estimated Duration</h3>
              <p className="text-sm text-gray-600">
                The scan typically takes 1-2 hours depending on network size.
              </p>
            </div>
          </div>

          <div className="flex items-start">
            <div className="flex-shrink-0 w-6 h-6 bg-yfitg-accent text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
              3
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">Report Generation</h3>
              <p className="text-sm text-gray-600">
                Once complete, an AI-generated executive report will be automatically delivered to YFITG.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-500">
            You can safely unplug the device after the scan completes. The e-ink display will show "Scan Complete ✓"
          </p>
        </div>
      </div>
    </div>
  )
}

