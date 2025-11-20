import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'YFITG Network Scout - Consent Portal',
  description: 'Authorize network security assessment',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

