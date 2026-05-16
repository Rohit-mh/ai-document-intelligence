import React, { useEffect, useState } from 'react'
import { Header, Footer } from '../components'
import { getHealth } from '../services'

export const MainLayout = ({ children }) => {
  const [systemStatus, setSystemStatus] = useState(null)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await getHealth()
        setSystemStatus(status)
      } catch (error) {
        console.error('Failed to fetch system status:', error)
      }
    }

    fetchStatus()
    const interval = setInterval(fetchStatus, 30000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex flex-col min-h-screen bg-zinc-950 text-zinc-100">
      <Header systemStatus={systemStatus} />
      <main className="flex-1 w-full max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
        {children}
      </main>
      <Footer />
    </div>
  )
}
