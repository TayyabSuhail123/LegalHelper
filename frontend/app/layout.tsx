import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'ContractCopilot - AI-Powered Legal Document Risk Scanner',
  description: 'Analyze legal contracts with AI precision. Upload your contract and get instant AI-powered analysis identifying risks, unfavorable terms, and actionable insights.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">{children}</body>
    </html>
  )
}
