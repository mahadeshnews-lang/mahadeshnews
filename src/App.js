import React, { useState, useEffect } from 'react';
// मान लीजिए कि आपकी CSS फ़ाइल सही है
// import './index.css'; 
// अन्य इंपोर्ट्स (जैसे Menu, Search, Bell, Users)
// यहाँ जोड़ें अगर आपको उनकी ज़रूरत है

const App = () => {
  const [loading, setLoading] = useState(true);
  const [articles, setArticles] = useState([]);
  const [headline, setHeadline] = useState("No Headline");
  const [error, setError] = useState(null);

  // आपकी पुरानी नकली न्यूज़ (Demo News) हटा दी गई है
  
  // यह useEffect हुक अब केवल MongoDB से डेटा खींचेगा
  useEffect(() => {
    // Vercel/Python Backend से डेटा खींचें (जो MongoDB से न्यूज़ लाएगा)
    fetch('/api/news/all')
      .then(res => {
        if (!res.ok) {
          throw new Error('Network response was not ok');
        }
        return res.json();
      })
      .then(data => {
        // मान लीजिए कि आपका बैकएंड डेटा को इस तरह भेजता है: { articles: [...], headline: "..." }
        if (data && data.articles) {
          setArticles(data.articles);
          setHeadline(data.headline || "Latest News");
        } else {
          // अगर API सफल है लेकिन डेटा खाली है
          setArticles([]);
          setHeadline("No News Found in Database");
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Fetching Error:", err);
        setError("Error loading news. Backend API might be down.");
        setArticles([]);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <h1 className="text-xl font-bold">न्यूज़ लोड हो रही है...</h1>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-100 text-red-700">
        <h1 className="text-xl font-bold">त्रुटि: {error}</h1>
        <p>कृपया सुनिश्चित करें कि GitHub Action (ऑटोमेशन) चला है और MongoDB में डेटा है।</p>
      </div>
    );
  }

  // यदि कोई समस्या नहीं है, तो मुख्य वेबसाइट दिखाएँ
  return (
    <div className="min-h-screen bg-gray-100 text-gray-900">
      
      {/* 1. TOP HEADER (RED) - इसमें बदलाव नहीं किया गया */}
      <header className="bg-red-700 text-white p-4">
        {/* आपका पुराना HEADER कोड यहाँ है */}
        <div className="container mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold">MAHADESH<span className="text-yellow-400">NEWS</span></h1>
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-3 rounded">LIVE TV</button>
        </div>
      </header>

      {/* 2. BREAKING NEWS TIKER - इसमें बदलाव नहीं किया गया */}
      <div className="bg-yellow-400 text-black py-2 px-4 overflow-hidden">
        <span className="font-bold mr-4">BREAKING</span>
        <span className="whitespace-nowrap">नया अपडेट: पुलिस भर्ती प्रक्रिया शुरू • पेट्रोल-डीजल के दाम बढ़े</span>
      </div>

      {/* 3. MAIN CONTENT (आपके पुराने कोड के अनुसार) */}
      <main className="container mx-auto p-4">
        
        {/* Categories / Tabs (आपके पुराने कोड के अनुसार) */}
        <div className="flex space-x-4 mb-4 overflow-x-auto pb-2 border-b">
          {['Top Stories', 'Jalna', 'Aurangabad', 'Maharashtra', 'India', 'World', 'Sports'].map(category => (
             <button key={category} className="bg-gray-200 hover:bg-gray-300 text-sm font-medium py-1 px-3 rounded-full border border-gray-400">
                {category}
             </button>
          ))}
        </div>

        {/* HEADLINE / FEATURED ARTICLE (पहली AI न्यूज़) */}
        <h2 className="text-xl font-bold mb-4">{headline}</h2>

        {/* ARTICLES GRID */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {articles.length > 0 ? (
            articles.map((article, index) => (
              // यह एक साधारण आर्टिकल डिस्प्ले कॉम्पोनेंट है
              <div key={index} className="bg-white rounded-lg shadow-lg overflow-hidden cursor-pointer hover:shadow-xl transition duration-300">
                <img src={article.image || 'https://via.placeholder.com/400x200?text=Mahadesh+News'} alt={article.title_hi || "News Image"} className="w-full h-48 object-cover"/>
                <div className="p-4">
                  {/* हम हिंदी शीर्षक दिखाने की कोशिश कर रहे हैं */}
                  <h3 className="text-lg font-bold mb-2">{article.title_hi || article.topic}</h3>
                  <p className="text-sm text-gray-600">पब्लिश: {new Date(article.timestamp).toLocaleDateString()}</p>
                </div>
              </div>
            ))
          ) : (
             <div className="col-span-3 text-center py-10 text-gray-500">
                <p>डेटाबेस में कोई नई AI-जनरेटेड न्यूज़ नहीं मिली।</p>
                <p>कृपया सुनिश्चित करें कि GitHub Action (ऑटोमेशन) सफलता पूर्वक चला है।</p>
            </div>
          )}
        </div>
      </main>
      {/* FOOTER - इसमें बदलाव नहीं किया गया */}
    </div>
  );
};

export default App;
 
