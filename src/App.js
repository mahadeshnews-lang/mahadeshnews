import React, { useState, useEffect } from 'react';
import { Menu, Search, Bell, Share2, MessageCircle, Clock } from 'lucide-react';

function App() {
  const [loading, setLoading] = useState(true);
  const [news, setNews] = useState([]);

  // Fake News for Demo (jab tak backend connect na ho)
  const demoNews = [
    {
      id: 1,
      title: "जालना में भारी बारिश की चेतावनी, प्रशासन ने जारी किया अलर्ट",
      category: "स्थानीय",
      image: "https://images.unsplash.com/photo-1541888946425-d81bb19240f5?w=800",
      time: "2 घंटे पहले"
    },
    {
      id: 2,
      title: "महाराष्ट्र सरकार की नई योजना: किसानों को मिलेगा बड़ा लाभ",
      category: "राज्य",
      image: "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=800",
      time: "4 घंटे पहले"
    },
    {
      id: 3,
      title: "क्रिकेट: भारतीय टीम ने रोमांचक मैच में जीत दर्ज की",
      category: "खेल",
      image: "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=800",
      time: "5 घंटे पहले"
    }
  ];

  useEffect(() => {
    // Backend check (This will now try to connect to your Python backend)
    fetch('/api/news/all')
      .then(res => res.json())
      .then(data => {
        if(data.success) {
          setNews(data.data.articles);
        } else {
          setNews(demoNews);
        }
        setLoading(false);
      })
      .catch(() => {
        setNews(demoNews);
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 font-sans">
      {/* 1. TOP HEADER (RED) */}
      <header className="bg-red-700 text-white sticky top-0 z-50 shadow-lg">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Menu className="h-6 w-6 cursor-pointer hover:text-yellow-400" />
            <h1 className="text-2xl font-bold tracking-tighter">
              MAHADESH<span className="text-yellow-400">NEWS</span>
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <Search className="h-5 w-5 cursor-pointer" />
            <Bell className="h-5 w-5 cursor-pointer" />
            <button className="bg-white text-red-700 px-4 py-1 rounded-full font-bold text-sm hover:bg-gray-200">
              LIVE TV
            </button>
          </div>
        </div>
      </header>

      {/* 2. BREAKING NEWS TICKER */}
      <div className="bg-yellow-400 text-black py-2 overflow-hidden flex items-center">
        <div className="bg-red-700 text-white px-4 py-1 font-bold text-sm ml-2 rounded skew-x-[-10deg]">
          BREAKING
        </div>
        <marquee className="font-semibold text-sm ml-4">
          • महाराष्ट्र में चुनाव की तारीखों का ऐलान • जालना: पुलिस भर्ती प्रक्रिया शुरू • पेट्रोल-डीजल के दामों में गिरावट •
        </marquee>
      </div>

      {/* 3. MAIN CONTENT */}
      <main className="container mx-auto p-4">
        {/* Category Chips */}
        <div className="flex gap-3 overflow-x-auto pb-4 scrollbar-hide">
          {['Top Stories', 'Jalna', 'Aurangabad', 'Maharashtra', 'India', 'World', 'Sports'].map((cat) => (
            <button key={cat} className="px-4 py-1 bg-white rounded-full text-sm font-medium hover:bg-red-50 border border-gray-200 whitespace-nowrap">
              {cat}
            </button>
          ))}
        </div>

        {/* News Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
          {/* Main Story (Big) */}
          <div className="md:col-span-2 relative group cursor-pointer overflow-hidden rounded-xl shadow-lg h-96">
            <img 
              src={news[0]?.image || demoNews[0].image} 
              alt="Main News" 
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            />
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-6">
              <span className="bg-red-600 text-white text-xs px-2 py-1 rounded mb-2 inline-block">
                {news[0]?.category || demoNews[0].category}
              </span>
              <h2 className="text-white text-3xl font-bold leading-tight">
                {news[0]?.title || demoNews[0].title}
              </h2>
              <div className="text-gray-300 text-sm mt-2 flex items-center">
                <Clock className="h-4 w-4 mr-1" /> {news[0]?.time || demoNews[0].time}
              </div>
            </div>
          </div>

          {/* Side Stories */}
          <div className="space-y-4">
            {news.slice(1, 4).map((item) => (
              <div key={item.id} className="bg-white p-3 rounded-xl shadow flex gap-3 cursor-pointer hover:shadow-md transition">
                <img src={item.image} alt="" className="w-24 h-24 object-cover rounded-lg flex-shrink-0" />
                <div className="flex flex-col justify-between">
                  <span className="text-red-600 text-xs font-bold">{item.category}</span>
                  <h3 className="font-semibold text-sm line-clamp-3 leading-snug">{item.title}</h3>
                  <div className="flex gap-3 text-gray-400 mt-2">
                    <Share2 className="h-4 w-4 hover:text-blue-500" />
                    <MessageCircle className="h-4 w-4 hover:text-green-500" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
    
