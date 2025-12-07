import { useState, useRef, useEffect } from 'react'
import './App.css'

// Import slot provider mapping
import slotProvidersData from '../slot_providers.json'

// Convert slot providers object to array, filtering to only include slots with images
// Image files should exist at public/images/{name} - filenames already include extensions
const availableSlots = Object.entries(slotProvidersData)
  .map(([filename, provider]) => {
    // filename already includes the extension (e.g., "gamomat-40-finest-xxl.png")
    // Extract the display name by removing the extension and converting from kebab-case
    let nameWithoutExt = filename.replace(/\.(jpg|png|gif|webp)$/, '');
    
    // Remove provider prefix if it exists at the start (e.g., "gamomat-" or "1x2gaming-")
    const providerSlug = provider
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .replace(/-+/g, '-');

    if (providerSlug) {
      const providerPattern = new RegExp(
        `^${providerSlug.replace(/-/g, '[-_\\s]*')}[-_\\s]*`,
        'i'
      );
      nameWithoutExt = nameWithoutExt.replace(providerPattern, '');
    }
    
    const displayName = nameWithoutExt
      .replace(/_/g, ' ')
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
      .trim()
      .replace(/\s+/g, ' ');
    
    return {
      name: displayName,
      provider,
      image: `/images/${filename}`
    };
  })
  .filter(slot => {
    // Only include slots that are likely to have images
    // This filters out slots without images on gamingslots.com
    return slot.name && slot.provider;
  });

// Note: To show only slots with available images, we rely on the image loading in the browser
// Slots without images will show a broken image icon
const NUM_SLOTS = availableSlots.length;

function App() {
  // Generate slots using the available images
  const fullSlots = availableSlots;

  // Get unique providers
  const providers = [...new Set(availableSlots.map(slot => slot.provider))].sort();
  
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [isSpinning, setIsSpinning] = useState(false);
  const [displaySlots, setDisplaySlots] = useState(() => fullSlots.slice(0, 5));
  const [bgTheme, setBgTheme] = useState('ocean');
  const [theme, setTheme] = useState('purple');
  const [showBonusHunt, setShowBonusHunt] = useState(false);
  const [bonusHuntCount, setBonusHuntCount] = useState(5);
  const [bonusHuntList, setBonusHuntList] = useState([]);
  const [bonusHuntData, setBonusHuntData] = useState({}); // Track bet size and payout per slot
  const [activeBonusHunt, setActiveBonusHunt] = useState(null); // Active bonus hunt view
  const [bonusHuntHistory, setBonusHuntHistory] = useState([]); // Persisted hunt history
  const [bonusHuntName, setBonusHuntName] = useState('');
  const [selectedProviders, setSelectedProviders] = useState(new Set(providers));
  const [shuffledSlots, setShuffledSlots] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const gridRef = useRef(null);
  const bonusHuntRef = useRef(null);

  // ---- Persistence helpers ----
  const STORAGE_KEY = 'slotselector-state-v1';
  const safeParse = (value, fallback) => {
    try {
      return JSON.parse(value);
    } catch (e) {
      return fallback;
    }
  };

  // Load persisted state once on mount
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return;

    const data = safeParse(raw, {});
    if (data.bgTheme) setBgTheme(data.bgTheme);
    if (Array.isArray(data.selectedProviders) && data.selectedProviders.length) {
      setSelectedProviders(new Set(data.selectedProviders));
    }
    if (typeof data.searchTerm === 'string') setSearchTerm(data.searchTerm);
    if (Array.isArray(data.bonusHuntList)) setBonusHuntList(data.bonusHuntList);
    if (data.bonusHuntData && typeof data.bonusHuntData === 'object') setBonusHuntData(data.bonusHuntData);
    if (data.activeBonusHunt) setActiveBonusHunt(true);
    if (Array.isArray(data.bonusHuntHistory)) setBonusHuntHistory(data.bonusHuntHistory);
    if (typeof data.bonusHuntName === 'string') setBonusHuntName(data.bonusHuntName);
  }, []);

  // Persist key state slices whenever they change
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const payload = {
      bgTheme,
      selectedProviders: Array.from(selectedProviders),
      searchTerm,
      bonusHuntList,
      bonusHuntData,
      activeBonusHunt,
      bonusHuntHistory,
      bonusHuntName,
    };
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  }, [bgTheme, selectedProviders, searchTerm, bonusHuntList, bonusHuntData, activeBonusHunt, bonusHuntHistory]);

  // Filter slots based on selected providers and search term
  const filteredSlots = fullSlots.filter(slot => 
    selectedProviders.has(slot.provider) && 
    slot.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Shuffle slots only when providers or search term change, not during spinning
  useEffect(() => {
    const newShuffledSlots = [...filteredSlots].sort(() => Math.random() - 0.5);
    setShuffledSlots(newShuffledSlots);
  }, [selectedProviders, searchTerm]);

  const handleProviderToggle = (provider) => {
    const newProviders = new Set(selectedProviders);
    if (newProviders.has(provider)) {
      newProviders.delete(provider);
    } else {
      newProviders.add(provider);
    }
    setSelectedProviders(newProviders);
  };

  const createParticles = (x, y) => {
    const particleCount = 15;
    for (let i = 0; i < particleCount; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle spark';
      
      const angle = (Math.PI * 2 * i) / particleCount;
      const velocity = 150 + Math.random() * 100;
      const tx = Math.cos(angle) * velocity;
      const ty = Math.sin(angle) * velocity;
      
      particle.style.left = x + 'px';
      particle.style.top = y + 'px';
      particle.style.setProperty('--tx', tx + 'px');
      particle.style.setProperty('--ty', ty + 'px');
      
      document.body.appendChild(particle);
      
      setTimeout(() => particle.remove(), 800);
    }
  };

  const spin = () => {
    if (isSpinning || filteredSlots.length === 0) return;
    setIsSpinning(true);
    
    // Create particle effect at button location
    const spinButton = document.querySelector('.spin-button');
    if (spinButton) {
      const rect = spinButton.getBoundingClientRect();
      createParticles(rect.left + rect.width / 2, rect.top + rect.height / 2);
    }
    
    // Random selection from filtered slots
    const randomIndex = Math.floor(Math.random() * filteredSlots.length);
    const winningSlot = filteredSlots[randomIndex];
    
    // Spin animation - reel spinning effect
    const spinDuration = 2500; // 2.5 seconds
    const cycleInterval = 100; // Change display every 100ms
    let cycles = 0;
    const totalCycles = spinDuration / cycleInterval;
    
    const spinInterval = setInterval(() => {
      // Generate 5 random slots to simulate reel spinning from filtered slots
      const newSlots = Array.from({ length: 5 }, () => filteredSlots[Math.floor(Math.random() * filteredSlots.length)]);
      setDisplaySlots(newSlots);
      cycles++;
      
      if (cycles >= totalCycles) {
        clearInterval(spinInterval);
        // Final position: winning slot in the middle
        setDisplaySlots(Array.from({ length: 5 }, (_, idx) => {
          if (idx === 2) return winningSlot;
          return filteredSlots[Math.floor(Math.random() * filteredSlots.length)];
        }));
        
        // Show modal after a brief pause
        setTimeout(() => {
          setSelectedSlot(winningSlot);
          setIsSpinning(false);
        }, 300);
      }
    }, cycleInterval);
  };

  const generateBonusHunt = () => {
    const count = Math.min(Math.max(bonusHuntCount, 1), filteredSlots.length);
    const selected = [];
    const usedIndices = new Set();
    
    while (selected.length < count) {
      const randomIndex = Math.floor(Math.random() * filteredSlots.length);
      if (!usedIndices.has(randomIndex)) {
        usedIndices.add(randomIndex);
        selected.push(filteredSlots[randomIndex]);
      }
    }
    
    setBonusHuntList(selected);
    
    // Initialize bonusHuntData with default values
    const newData = {};
    selected.forEach((slot, idx) => {
      newData[idx] = { betSize: '1.00', payout: '0.00' };
    });
    setBonusHuntData(newData);
    
    // Switch to active bonus hunt view
    setActiveBonusHunt(true);
    setShowBonusHunt(false);

    // Append to history (most recent first, cap at 50 entries)
    const totalBet = Object.values(newData).reduce((sum, data) => sum + (parseFloat(data.betSize) || 0), 0);
    const totalPayout = Object.values(newData).reduce((sum, data) => sum + (parseFloat(data.payout) || 0), 0);
    const entry = {
      id: Date.now(),
      createdAt: new Date().toISOString(),
      slots: selected.map((slot) => ({ name: slot.name, provider: slot.provider })),
      totalBet,
      totalPayout,
    };
    setBonusHuntHistory((prev) => [entry, ...prev].slice(0, 50));
  };

  const saveCurrentBonusHunt = () => {
    if (!bonusHuntList.length) return;
    const totalBet = Object.values(bonusHuntData).reduce((sum, data) => sum + (parseFloat(data?.betSize) || 0), 0);
    const totalPayout = Object.values(bonusHuntData).reduce((sum, data) => sum + (parseFloat(data?.payout) || 0), 0);
    const entry = {
      id: Date.now(),
      name: bonusHuntName?.trim() || 'Untitled Hunt',
      createdAt: new Date().toISOString(),
      slots: bonusHuntList,
      data: bonusHuntData,
      totalBet,
      totalPayout,
    };
    setBonusHuntHistory((prev) => [entry, ...prev].slice(0, 50));
  };

  const loadBonusHunt = (entry) => {
    if (!entry) return;
    setBonusHuntList(entry.slots || []);
    setBonusHuntData(entry.data || {});
    setBonusHuntName(entry.name || '');
    setActiveBonusHunt(true);
    setShowBonusHunt(false);
  };

  return (
    <div className="app-wrapper" data-bg-theme={bgTheme}>
      <nav className="top-nav">
        <div className="nav-left">
          <span className="brand">SlotSelector</span>
          <span className="tag">Beta</span>
        </div>
        <div className="nav-actions">
          <button
            className="nav-btn"
            onClick={() => {
              if (gridRef.current) {
                gridRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
              }
            }}
          >
            Slots
          </button>
          <button
            className="nav-btn"
            onClick={() => setShowBonusHunt(true)}
          >
            Bonus Hunt
          </button>
          <button
            className="nav-btn"
            onClick={() => {
              if (bonusHuntRef.current) {
                bonusHuntRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
              }
              setShowBonusHunt(true);
            }}
          >
            Create / Load
          </button>
          {activeBonusHunt && (
            <button
              className="nav-btn highlight"
              onClick={() => setActiveBonusHunt(true)}
            >
              Active Hunt
            </button>
          )}
        </div>
      </nav>
      {activeBonusHunt ? (
        // Active Bonus Hunt Page
        <div className="bonus-hunt-page">
          <div className="bonus-hunt-page-header">
            <h1>🎁 Bonus Hunt</h1>
            <button 
              className="close-bonus-hunt-page-btn" 
              onClick={() => {
                setActiveBonusHunt(null);
                setBonusHuntList([]);
                setBonusHuntData({});
              }}
            >
              ✕ Clear Bonus Hunt
            </button>
          </div>

          <div className="bonus-hunt-page-content">
            <div className="bonus-hunt-slots-grid">
              {bonusHuntList.map((slot, idx) => (
                <div key={idx} className="bonus-hunt-page-item">
                  <div className="bonus-hunt-page-image-wrapper">
                    <span className="bonus-hunt-page-number">{idx + 1}</span>
                    <img src={slot.image} alt={slot.name} className="bonus-hunt-page-image" />
                  </div>
                  
                  <div className="bonus-hunt-page-details">
                    <h3 className="bonus-hunt-page-slot-name">{slot.name}</h3>
                    <p className="bonus-hunt-page-provider">{slot.provider}</p>
                  </div>

                  <div className="bonus-hunt-page-inputs">
                    <div className="page-input-group">
                      <label>Bet Size</label>
                      <div className="input-wrapper">
                        <span className="currency">€</span>
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          value={bonusHuntData[idx]?.betSize || '0.00'}
                          onChange={(e) => setBonusHuntData({
                            ...bonusHuntData,
                            [idx]: { ...bonusHuntData[idx], betSize: e.target.value }
                          })}
                          className="page-input-field"
                        />
                      </div>
                    </div>

                    <div className="page-input-group">
                      <label>Payout</label>
                      <div className="input-wrapper">
                        <span className="currency">€</span>
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          value={bonusHuntData[idx]?.payout || '0.00'}
                          onChange={(e) => setBonusHuntData({
                            ...bonusHuntData,
                            [idx]: { ...bonusHuntData[idx], payout: e.target.value }
                          })}
                          className="page-input-field"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="bonus-hunt-page-summary">
              <div className="summary-card">
                <div className="summary-item">
                  <span className="summary-label">Total Slots</span>
                  <span className="summary-value">{bonusHuntList.length}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Total Bet</span>
                  <span className="summary-value">€{Object.values(bonusHuntData).reduce((sum, data) => sum + (parseFloat(data.betSize) || 0), 0).toFixed(2)}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Total Payout</span>
                  <span className="summary-value">€{Object.values(bonusHuntData).reduce((sum, data) => sum + (parseFloat(data.payout) || 0), 0).toFixed(2)}</span>
                </div>
                <div className="summary-item highlight">
                  <span className="summary-label">Net Result</span>
                  <span className="summary-value">{(() => {
                    const totalBet = Object.values(bonusHuntData).reduce((sum, data) => sum + (parseFloat(data.betSize) || 0), 0);
                    const totalPayout = Object.values(bonusHuntData).reduce((sum, data) => sum + (parseFloat(data.payout) || 0), 0);
                    const net = totalPayout - totalBet;
                    return `€${net.toFixed(2)}`;
                  })()}</span>
                </div>
              </div>

              <div className="bonus-hunt-save">
                <input
                  type="text"
                  value={bonusHuntName}
                  onChange={(e) => setBonusHuntName(e.target.value)}
                  placeholder="Name this bonus hunt"
                  className="bonus-hunt-name-input"
                />
                <button
                  className="save-bonus-hunt-btn"
                  onClick={saveCurrentBonusHunt}
                  disabled={!bonusHuntList.length}
                >
                  💾 Save Hunt
                </button>
              </div>

              {bonusHuntHistory.length > 0 && (
                <div className="saved-hunts">
                  <div className="saved-hunts-header">
                    <h4>Saved Hunts</h4>
                    <span>{bonusHuntHistory.length} saved</span>
                  </div>
                  <div className="saved-hunts-list">
                    {bonusHuntHistory.slice(0, 6).map((entry) => (
                      <div key={entry.id} className="saved-hunt-card">
                        <div className="saved-hunt-meta">
                          <div className="saved-hunt-name">{entry.name}</div>
                          <div className="saved-hunt-sub">{new Date(entry.createdAt).toLocaleString()}</div>
                        </div>
                        <div className="saved-hunt-stats">
                          <span>{entry.slots?.length || 0} slots</span>
                          <span>€{(entry.totalBet ?? 0).toFixed ? entry.totalBet.toFixed(2) : Number(entry.totalBet || 0).toFixed(2)}</span>
                        </div>
                        <button className="load-hunt-btn" onClick={() => loadBonusHunt(entry)}>
                          Load
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <button
                className="copy-bonus-hunt-details-btn"
                onClick={() => {
                  const text = bonusHuntList.map((slot, idx) => {
                    const data = bonusHuntData[idx] || { betSize: '0.00', payout: '0.00' };
                    return `${idx + 1}. ${slot.name} (${slot.provider}) - Bet: €${data.betSize} | Payout: €${data.payout}`;
                  }).join('\n');
                  navigator.clipboard.writeText(text);
                  alert('Bonus hunt details copied to clipboard!');
                }}
              >
                📋 Copy All Details
              </button>
            </div>
          </div>
        </div>
      ) : (
        // Main App View
        <div className="app">
          <div className="left-panel">
            <div className="counter-wrapper">
              <div className="slot-counter">
                <div className="counter-item">
                  <div className="counter-label">Total</div>
                  <div className="counter-display">{NUM_SLOTS}</div>
                </div>
              </div>
              <div className="slot-counter">
                <div className="counter-item active">
                  <div className="counter-label">Showing</div>
                  <div className="counter-display">{filteredSlots.length}</div>
                </div>
              </div>
            </div>
          
          <div className="provider-filter">
            <h3>Providers</h3>
            <div className="provider-list">
              {providers.map(provider => (
                <label key={provider} className="provider-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedProviders.has(provider)}
                    onChange={() => handleProviderToggle(provider)}
                  />
                  <span>{provider}</span>
                  <span className="provider-count">
                    ({fullSlots.filter(s => s.provider === provider).length})
                  </span>
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="center-content" ref={gridRef}>
          <div className="search-bar-wrapper">
            <input
              type="text"
              className="search-bar"
              placeholder="🔍 Search slots..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            {searchTerm && (
              <button 
                className="search-clear-btn"
                onClick={() => setSearchTerm('')}
              >
                ✕
              </button>
            )}
          </div>
          <div className="grid-container">
          {!isSpinning && (
            <div className="grid-item demo-item">
              <div className="demo-content">
                <div className="demo-text">🎰</div>
              </div>
            </div>
          )}
          {shuffledSlots.map((slot, index) => (
            <div key={index} className="grid-item" data-provider={slot.provider}>
              <img src={slot.image} alt={slot.name} />
              <div className="grid-item-label">
                <span className="slot-name">{slot.name}</span>
                <span className="slot-provider">{slot.provider}</span>
              </div>
            </div>
          ))}
        </div>
        <div className="bonus-hunt-section" ref={bonusHuntRef}>
          <button className="bonus-hunt-button-stretched" onClick={() => {
            setShowBonusHunt(true);
            setBonusHuntList([]);
          }} disabled={filteredSlots.length === 0}>
            🎁 Create Bonus Hunt
          </button>
        </div>
        </div>
        
        <div className="right-panel">
          <div className="button-container">
            <button className="spin-button" onClick={spin} disabled={isSpinning || filteredSlots.length === 0}>
              <span className={`spin-icon ${isSpinning ? 'spinning' : ''}`}>✨</span>
              <span>Lucky<br/>Pick</span>
            </button>
          {(displaySlots || isSpinning) && (
            <div className={`spin-reel ${isSpinning ? 'spinning' : ''}`}>
              <div className="reel-container">
                {displaySlots.map((slot, idx) => (
                  <div key={idx} className={`reel-item ${idx === 2 ? 'center' : ''}`}>
                      <img src={slot.image} alt={slot.name} />
                      {slot && (
                        <div className="reel-item-label">
                          <span className="reel-slot-name">{slot.name}</span>
                          <span className="reel-slot-provider">{slot.provider}</span>
                        </div>
                      )}
                    </div>
                ))}
              </div>
              <div className="reel-shine"></div>
              <div className="reel-glow"></div>
            </div>
          )}
          </div>
        </div>

        <div className="bg-theme-selector">
          <label>Background Theme:</label>
          <div className="bg-theme-buttons">
            <button className={`bg-theme-btn ${bgTheme === 'galaxy' ? 'active' : ''}`} onClick={() => setBgTheme('galaxy')} title="Galaxy" style={{background: 'linear-gradient(135deg, #1a0033, #2d0066)'}}></button>
            <button className={`bg-theme-btn ${bgTheme === 'aurora' ? 'active' : ''}`} onClick={() => setBgTheme('aurora')} title="Aurora" style={{background: 'linear-gradient(135deg, #0d5f4f, #00ff88)'}}></button>
            <button className={`bg-theme-btn ${bgTheme === 'ocean' ? 'active' : ''}`} onClick={() => setBgTheme('ocean')} title="Ocean" style={{background: 'linear-gradient(135deg, #001f3f, #0099ff)'}}></button>
            <button className={`bg-theme-btn ${bgTheme === 'neon' ? 'active' : ''}`} onClick={() => setBgTheme('neon')} title="Neon" style={{background: 'linear-gradient(135deg, #3d0099, #ff00ff)'}}></button>
            <button className={`bg-theme-btn ${bgTheme === 'fire' ? 'active' : ''}`} onClick={() => setBgTheme('fire')} title="Fire" style={{background: 'linear-gradient(135deg, #ff6600, #ffcc00)'}}></button>
            <button className={`bg-theme-btn ${bgTheme === 'cosmic' ? 'active' : ''}`} onClick={() => setBgTheme('cosmic')} title="Cosmic" style={{background: 'linear-gradient(135deg, #1a1a2e, #16213e)'}}></button>
            <button className={`bg-theme-btn ${bgTheme === 'midnight' ? 'active' : ''}`} onClick={() => setBgTheme('midnight')} title="Midnight" style={{background: 'linear-gradient(135deg, #0a0a1a, #1a0a2e)'}}></button>
            
            {/* New Theme Buttons */}
            <button className={`bg-theme-btn ${bgTheme === 'cyberpunk' ? 'active' : ''}`} onClick={() => setBgTheme('cyberpunk')} title="Cyberpunk" style={{background: 'linear-gradient(135deg, #2a1a4e, #3a2a6e)'}}></button>
            <button className={`bg-theme-btn ${bgTheme === 'lava' ? 'active' : ''}`} onClick={() => setBgTheme('lava')} title="Lava" style={{background: 'linear-gradient(135deg, #ff3300, #ff6600)'}}></button>
            <button className={`bg-theme-btn ${bgTheme === 'space' ? 'active' : ''}`} onClick={() => setBgTheme('space')} title="Space" style={{background: 'linear-gradient(135deg, #1a0033, #000000)'}}></button>
            <button className={`bg-theme-btn ${bgTheme === 'volcanic' ? 'active' : ''}`} onClick={() => setBgTheme('volcanic')} title="Volcanic" style={{background: 'linear-gradient(135deg, #5a3a2a, #8a4a3a)'}}></button>
            <button className={`bg-theme-btn ${bgTheme === 'lights' ? 'active' : ''}`} onClick={() => setBgTheme('lights')} title="Aurora Lights" style={{background: 'linear-gradient(135deg, #1a3a6a, #2a6a9a)'}}></button>
            <button className={`bg-theme-btn ${bgTheme === 'void' ? 'active' : ''}`} onClick={() => setBgTheme('void')} title="Void" style={{background: 'linear-gradient(135deg, #0a0a15, #050508)'}}></button>
            <button className={`bg-theme-btn ${bgTheme === 'plasma' ? 'active' : ''}`} onClick={() => setBgTheme('plasma')} title="Plasma" style={{background: 'linear-gradient(135deg, #1a0a2e, #3a2a6e)'}}></button>
            <button className={`bg-theme-btn ${bgTheme === 'grid' ? 'active' : ''}`} onClick={() => setBgTheme('grid')} title="Neon Grid" style={{background: 'linear-gradient(135deg, #0a0a1a, #00ffff)'}}></button>
            <button className={`bg-theme-btn ${bgTheme === 'emerald' ? 'active' : ''}`} onClick={() => setBgTheme('emerald')} title="Emerald" style={{background: 'linear-gradient(135deg, #0d3622, #2a8b6a)'}}></button>
          </div>
        </div>

        {selectedSlot && (
          <div className="modal-overlay" onClick={() => setSelectedSlot(null)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <h2>🎉 Winner! 🎉</h2>
              <img src={selectedSlot.image} alt={selectedSlot.name} />
              <p>{selectedSlot.name}</p>
              <p>Provider: {selectedSlot.provider}</p>
              <button onClick={() => setSelectedSlot(null)}>Spin Again</button>
            </div>
          </div>
        )}

        {showBonusHunt && (
          <div className="modal-overlay" onClick={() => setShowBonusHunt(false)}>
            <div className="modal-content bonus-hunt-modal" onClick={(e) => e.stopPropagation()}>
              <h2>🎁 Create Bonus Hunt</h2>
              
              {bonusHuntList.length === 0 ? (
                <>
                  <p className="bonus-hunt-description">How many slots would you like to add to your bonus hunt?</p>
                  <div className="bonus-hunt-input-group">
                    <input
                      type="number"
                      min="1"
                      max={NUM_SLOTS}
                      value={bonusHuntCount}
                      onChange={(e) => setBonusHuntCount(Math.max(1, parseInt(e.target.value) || 1))}
                      className="bonus-hunt-input"
                    />
                    <button className="bonus-hunt-generate-btn" onClick={generateBonusHunt}>
                      Generate Hunt
                    </button>
                  </div>
                  <p className="bonus-hunt-hint">Enter a number between 1 and {NUM_SLOTS}</p>
                </>
              ) : null}
              
              <button className="close-bonus-hunt-btn" onClick={() => setShowBonusHunt(false)}>
                Close
              </button>
            </div>
          </div>
        )}
      </div>
      )}
    </div>
  )
}

export default App
