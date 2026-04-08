import './globals.css'

export const metadata = {
  title: 'JARVIS Console',
  description: 'OpenRouter-first autonomous assistant UI'
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
