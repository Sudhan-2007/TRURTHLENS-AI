import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import Footer from './Footer'

function OfficialBanner() {
  return (
    <div className="bg-black text-white text-xs py-1 px-4 flex items-center justify-between">
      <div className="flex items-center space-x-2">
        <span role="img" aria-label="flag">🇺🇸</span>
        <span>An official website of the United States government</span>
      </div>
      <div>
        <a href="#" className="underline hover:text-gray-300">Here's how you know</a>
      </div>
    </div>
  )
}

export default function Layout() {
  return (
    <div className="flex min-h-screen flex-col bg-white">
      <OfficialBanner />
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
