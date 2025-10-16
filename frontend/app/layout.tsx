import './globals.css';
import type { Metadata, Viewport } from 'next';

export const metadata: Metadata = {
  title: 'ContractCopilot - AI-Powered Legal Document Risk Scanner',
  description:
    'Analyze legal contracts with AI precision. Upload your contract and get instant AI-powered analysis identifying risks, unfavorable terms, and actionable insights.',
  keywords:
    'contract analysis, legal AI, document scanner, risk assessment, legal tech',
  authors: [{ name: 'ContractCopilot Team' }],
  openGraph: {
    title: 'ContractCopilot - AI-Powered Legal Document Risk Scanner',
    description:
      'Analyze legal contracts with AI precision. Upload your contract and get instant AI-powered analysis identifying risks, unfavorable terms, and actionable insights.',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ContractCopilot - AI-Powered Legal Document Risk Scanner',
    description:
      'Analyze legal contracts with AI precision. Upload your contract and get instant AI-powered analysis identifying risks, unfavorable terms, and actionable insights.',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
