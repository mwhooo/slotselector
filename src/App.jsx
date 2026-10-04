import { useState, useRef, useEffect } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'
import './App.css'
import { supabase } from './lib/supabase'

// Import slot provider mapping
import slotProvidersData from '../data/slot_providers.json'
import slotBetLimitsData from '../data/1x2gaming_711_bet_limits.json'
import threeOaksBetLimitsData from '../data/3oaks_711_bet_limits.json'
import amusnetCatalogData from '../data/amusnet_711_catalog.json'
import atomicSlotLabCatalogData from '../data/atomic_slot_lab_711_catalog.json'
import bfGamesCatalogData from '../data/bf_games_711_catalog.json'
import bgamingCatalogData from '../data/bgaming_711_catalog.json'
import bluberiCatalogData from '../data/bluberi_711_catalog.json'
import boomingGamesCatalogData from '../data/booming_games_711_catalog.json'
import boomerangCatalogData from '../data/boomerang_711_catalog.json'
import egtDigitalCatalogData from '../data/egt_digital_711_catalog.json'
import elkStudiosCatalogData from '../data/elk_studios_711_catalog.json'
import endorphinaCatalogData from '../data/endorphina_711_catalog.json'
import gamomatCatalogData from '../data/gamomat_711_catalog.json'
import gamesGlobalCatalogData from '../data/games_global_711_catalog.json'
import greentubeCatalogData from '../data/greentube_711_catalog.json'
import hacksawCatalogData from '../data/hacksaw_711_catalog.json'
import indigoMagicCatalogData from '../data/indigo_magic_711_catalog.json'
import inspiredCatalogData from '../data/inspired_711_catalog.json'
import kajotGamesCatalogData from '../data/kajot_711_catalog.json'
import kalambaCatalogData from '../data/kalamba_711_catalog.json'
import kingShowGamesCatalogData from '../data/king_show_games_711_catalog.json'
import mgaGamesCatalogData from '../data/mga_games_711_catalog.json'
import merkurCatalogData from '../data/merkur_gaming_711_catalog.json'
import netentCatalogData from '../data/netent_711_catalog.json'
import noLimitCityCatalogData from '../data/nolimit_city_711_catalog.json'
import oryxGamingCatalogData from '../data/oryx_gaming_711_catalog.json'
import playngoCatalogData from '../data/playngo_711_catalog.json'
import playsonCatalogData from '../data/playson_711_catalog.json'
import pushGamingCatalogData from '../data/push_gaming_711_catalog.json'
import pragmaticPlayCatalogData from '../data/pragmatic_play_711_catalog.json'
import redRakeGamingCatalogData from '../data/red_rake_gaming_711_catalog.json'
import redTigerCatalogData from '../data/red_tiger_711_catalog.json'
import relaxGamingCatalogData from '../data/relax_gaming_711_catalog.json'
import rubyplayCatalogData from '../data/rubyplay_711_catalog.json'
import silverBulletCatalogData from '../data/silver_bullet_711_catalog.json'
import slingoCatalogData from '../data/slingo_711_catalog.json'
import smartsoftGamingCatalogData from '../data/smartsoft_gaming_711_catalog.json'
import spinomenalCatalogData from '../data/spinomenal_711_catalog.json'
import stakelogicCatalogData from '../data/stakelogic_711_catalog.json'
import swinttCatalogData from '../data/swintt_711_catalog.json'
import synotCatalogData from '../data/synot_711_catalog.json'
import tadaGamingCatalogData from '../data/tada_gaming_711_catalog.json'
import thunderkickCatalogData from '../data/thunderkick_711_catalog.json'
import wazdanCatalogData from '../data/wazdan_711_catalog.json'
import yggdrasilCatalogData from '../data/yggdrasil_711_catalog.json'
import slotRtpData from '../data/slot_rtp.json'

const normalizeSlotName = (name) => name
  .toLowerCase()
  .replace(/&/g, 'and')
  .replace(/tm$/, '')
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '')

const getSlotCasinoLinks = (slot, linksByProviderAndName) => {
  const links = linksByProviderAndName.get(`${slot.provider}:${normalizeSlotName(slot.name)}`)
  return Object.entries(links ?? {}).map(([casino, url]) => ({ casino, url }))
}

const APP_STATE_KEY = 'slotselector-state-v1'

const createDefaultAppState = (providers) => ({
  selectedProviders: [...providers],
  searchTerm: '',
  maxMinBet: null,
  minRtp: null,
  bonusHuntList: [],
  bonusHuntData: {},
  activeBonusHunt: null,
  bonusHuntHistory: [],
  bonusHuntName: '',
})

const getStateStorageKey = (userId) => userId
  ? `${APP_STATE_KEY}:user:${userId}`
  : APP_STATE_KEY

const parseStoredState = (raw, fallback = null) => {
  try {
    return raw ? JSON.parse(raw) : fallback
  } catch {
    return fallback
  }
}

const stateTimestamp = (state) => Date.parse(state?.updatedAt ?? '') || 0

const mergeAccountState = (userState, guestState, cloudState, defaultState) => {
  const baseState = userState && stateTimestamp(userState) > stateTimestamp(cloudState)
    ? userState
    : cloudState || userState || guestState || defaultState
  const historyById = new Map()

  const historyStates = [cloudState, guestState, userState]
    .filter(Boolean)
    .sort((left, right) => stateTimestamp(left) - stateTimestamp(right))

  historyStates.forEach((state) => {
    (Array.isArray(state.bonusHuntHistory) ? state.bonusHuntHistory : []).forEach((entry) => {
      const id = `${entry.id ?? ''}:${entry.createdAt ?? ''}:${entry.name ?? ''}`
      historyById.set(id, entry)
    })
  })

  return {
    ...baseState,
    bonusHuntHistory: [...historyById.values()]
      .sort((left, right) => Date.parse(right.createdAt ?? '') - Date.parse(left.createdAt ?? ''))
      .slice(0, 50),
  }
}

const restoreAppState = (data, providers, setters) => {
  const state = data ?? {}
  const slots = Array.isArray(state.bonusHuntList) ? state.bonusHuntList : []

  setters.setSelectedProviders(new Set(
    Array.isArray(state.selectedProviders) ? state.selectedProviders : providers,
  ))
  setters.setSearchTerm(typeof state.searchTerm === 'string' ? state.searchTerm : '')
  setters.setMaxMinBet(state.maxMinBet === null || Number.isFinite(state.maxMinBet) ? state.maxMinBet : null)
  setters.setMinRtp(state.minRtp === null || Number.isFinite(state.minRtp) ? state.minRtp : null)
  setters.setBonusHuntList(slots)
  setters.setBonusHuntData(ensureBonusHuntBetSizes(slots, state.bonusHuntData))
  setters.setActiveBonusHunt(state.activeBonusHunt || slots.length ? true : null)
  setters.setBonusHuntHistory(Array.isArray(state.bonusHuntHistory) ? state.bonusHuntHistory : [])
  setters.setBonusHuntName(typeof state.bonusHuntName === 'string' ? state.bonusHuntName : '')
}

const slotBetLimitsByName = new Map(
  [
    ...Object.entries(slotBetLimitsData),
    ...Object.entries(threeOaksBetLimitsData),
    ...amusnetCatalogData.map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...atomicSlotLabCatalogData.map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...bfGamesCatalogData.map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...bgamingCatalogData.map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...bluberiCatalogData.map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...boomingGamesCatalogData.map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...boomerangCatalogData.map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...egtDigitalCatalogData.map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...elkStudiosCatalogData.map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...endorphinaCatalogData.map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...gamomatCatalogData.map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...gamesGlobalCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...greentubeCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...hacksawCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...indigoMagicCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...inspiredCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...kajotGamesCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...kalambaCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...kingShowGamesCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...merkurCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...mgaGamesCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...netentCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...noLimitCityCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...oryxGamingCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...playngoCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...playsonCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...pushGamingCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...pragmaticPlayCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...redRakeGamingCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...redTigerCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...relaxGamingCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...rubyplayCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...silverBulletCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...slingoCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...smartsoftGamingCatalogData
      .filter(({ name, minBet, maxBet }) => name && (Number.isFinite(minBet) || Number.isFinite(maxBet)))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...spinomenalCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...stakelogicCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...swinttCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...synotCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...tadaGamingCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...thunderkickCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...wazdanCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
    ...yggdrasilCatalogData
      .filter(({ minBet, maxBet }) => Number.isFinite(minBet) || Number.isFinite(maxBet))
      .map(({ name, minBet, maxBet }) => [name, [minBet, maxBet]]),
  ].map(([name, [minBet, maxBet]]) => [
    normalizeSlotName(name),
    { minBet, maxBet },
  ])
)
const slotRtpByProviderAndName = new Map(
  Object.entries(slotRtpData).flatMap(([provider, slots]) =>
    Object.entries(slots).map(([name, rtp]) => [
      `${provider}:${normalizeSlotName(name)}`,
      rtp,
    ])
  )
)

// Convert slot providers object to array, filtering to only include slots with images
// Image files should exist at public/images/{name} - filenames already include extensions
const availableSlots = Object.entries(slotProvidersData)
  .map(([filename, provider]) => {
    // filename already includes the extension (e.g., "gamomat-40-finest-xxl.png")
    // Extract the display name by removing the extension and converting from kebab-case
    let nameWithoutExt = filename.replace(/\.(jpe?g|png|gif|webp)$/i, '');
    
    // Remove provider prefix if it exists at the start (e.g., "gamomat-" or "1x2gaming-")
    const providerSlug = provider
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .replace(/-+/g, '-');

    if (providerSlug) {
      const providerPatterns = [...new Set([
        providerSlug.replace(/-/g, '[-_\\s]*'),
        providerSlug.replace(/-/g, ''),
        providerSlug.split('-')[0],
      ])].sort((left, right) => right.length - left.length);
      for (const pattern of providerPatterns) {
        nameWithoutExt = nameWithoutExt.replace(new RegExp(`^${pattern}[-_\\s]*`, 'i'), '');
      }
    }
    
    const displayName = nameWithoutExt
      .replace(/_/g, ' ')
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
      .trim()
      .replace(/\s+/g, ' ');
    
    const betLimits = slotBetLimitsByName.get(normalizeSlotName(displayName));
    const rtp = slotRtpByProviderAndName.get(`${provider}:${normalizeSlotName(displayName)}`);

    return {
      name: displayName,
      provider,
      image: `/images/${filename}`,
      ...(betLimits || {}),
      ...(rtp != null ? { rtp } : {}),
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
const availableSlotByImage = new Map(availableSlots.map(slot => [slot.image, slot]));
const getSlotRtp = (slot) => slot.rtp ?? availableSlotByImage.get(slot.image)?.rtp;

const getSlotBetLimits = (slot) => {
  const availableSlot = availableSlotByImage.get(slot.image);
  return {
    minBet: slot.minBet ?? availableSlot?.minBet ?? 0.10,
    maxBet: slot.maxBet ?? availableSlot?.maxBet ?? Number.POSITIVE_INFINITY,
  };
};

const ensureBonusHuntBetSizes = (slots, data = {}) => Object.fromEntries(
  slots.map((slot, index) => {
    const current = data[index] ?? {};
    const betSize = Number.parseFloat(current.betSize);
    const normalizedBetSize = Number.isFinite(betSize) && betSize > 0
      ? betSize.toFixed(2)
      : getSlotBetLimits(slot).minBet.toFixed(2);
    return [index, { ...current, betSize: normalizedBetSize }];
  })
);

const formatStakeValue = (amount) => {
  if (!Number.isFinite(amount)) return '\u2014';
  const minimumFractionDigits = Number.isInteger(amount) ? 0 : amount < 1 ? 2 : 1;
  return amount.toLocaleString('en-US', { minimumFractionDigits, maximumFractionDigits: 2 });
};

const formatRtpValue = (rtp) => Number.isFinite(rtp)
  ? `${rtp.toLocaleString('en-US', { maximumFractionDigits: 2 })}%`
  : '\u2014';

function BonusHuntThumbnail({ slot }) {
  const [imageFailed, setImageFailed] = useState(false);
  const initials = slot.name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase();

  if (imageFailed || !slot.image) {
    return (
      <div className="bonus-hunt-thumb-fallback" role="img" aria-label={`${slot.name} thumbnail unavailable`}>
        {initials}
      </div>
    );
  }

  return (
    <img
      src={slot.image}
      alt={slot.name}
      className="bonus-hunt-thumb"
      onError={() => setImageFailed(true)}
    />
  );
}

const REEL_SLOT_COUNT = 7;
const REEL_CENTER_INDEX = Math.floor(REEL_SLOT_COUNT / 2);

function LuckyPickReel({ initialSlots, slots, winningSlot, spinId, isSpinning, onFinish }) {
  const [displaySlots, setDisplaySlots] = useState(initialSlots);
  const slotsRef = useRef(slots);
  const winningSlotRef = useRef(winningSlot);
  const onFinishRef = useRef(onFinish);

  useEffect(() => {
    slotsRef.current = slots;
    winningSlotRef.current = winningSlot;
    onFinishRef.current = onFinish;
  }, [slots, winningSlot, onFinish]);

  useEffect(() => {
    if (!isSpinning) return undefined;

    const spinInterval = window.setInterval(() => {
      const availableSlots = slotsRef.current;
      if (!availableSlots.length) return;
      setDisplaySlots(Array.from({ length: REEL_SLOT_COUNT }, () =>
        availableSlots[Math.floor(Math.random() * availableSlots.length)]
      ));
    }, 100);

    const spinTimeout = window.setTimeout(() => {
      const availableSlots = slotsRef.current;
      const winner = winningSlotRef.current;
      if (winner) {
        setDisplaySlots(Array.from({ length: REEL_SLOT_COUNT }, (_, index) => {
          if (index === REEL_CENTER_INDEX || !availableSlots.length) return winner;
          return availableSlots[Math.floor(Math.random() * availableSlots.length)];
        }));
      }
      onFinishRef.current(winner);
    }, 1000);

    return () => {
      window.clearInterval(spinInterval);
      window.clearTimeout(spinTimeout);
    };
  }, [isSpinning, spinId]);

  return (
    <div
      className={`spin-reel ${isSpinning ? 'spinning' : ''}`}
      style={{ '--reel-slot-count': REEL_SLOT_COUNT }}
    >
      <div className="reel-container">
        {displaySlots.map((slot, index) => (
          <div key={index} className={`reel-item ${index === REEL_CENTER_INDEX ? 'center' : ''}`}>
            <img src={slot.image} alt={slot.name} />
            <div className="reel-item-label">
              <span className="reel-slot-name">{slot.name}</span>
              <span className="reel-slot-provider">{slot.provider}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="reel-shine"></div>
      <div className="reel-glow"></div>
    </div>
  );
}

function App() {
  // Generate slots using the available images
  const fullSlots = availableSlots;

  // Get unique providers
  const providers = [...new Set(availableSlots.map(slot => slot.provider))].sort();
  
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [isSpinning, setIsSpinning] = useState(false);
  const [spinWinner, setSpinWinner] = useState(null);
  const [spinId, setSpinId] = useState(0);
  const bgTheme = 'galaxy';
  const [showHelp, setShowHelp] = useState(false);
  const [showBonusHunt, setShowBonusHunt] = useState(false);
  const [bonusHuntCount, setBonusHuntCount] = useState(5);
  const [bonusHuntList, setBonusHuntList] = useState([]);
  const [bonusHuntData, setBonusHuntData] = useState({}); // Track bet size and payout per slot
  const [activeBonusHunt, setActiveBonusHunt] = useState(null); // Active bonus hunt view
  const [bonusHuntHistory, setBonusHuntHistory] = useState([]); // Persisted hunt history
  const [authUser, setAuthUser] = useState(null);
  const [authReady, setAuthReady] = useState(!supabase);
  const [authBusy, setAuthBusy] = useState(false);
  const [authMessage, setAuthMessage] = useState('');
  const [cloudSyncStatus, setCloudSyncStatus] = useState('guest');
  const [loadedStorageKey, setLoadedStorageKey] = useState(null);
  const [cloudStateLoadedFor, setCloudStateLoadedFor] = useState(null);
  const [persistedPayload, setPersistedPayload] = useState(null);
  const [bonusHuntName, setBonusHuntName] = useState('');
  const [bonusHuntSaveMessage, setBonusHuntSaveMessage] = useState(null);
  const [bonusHuntAddMessage, setBonusHuntAddMessage] = useState('');
  const [slot711LinksByProviderAndName, setSlot711LinksByProviderAndName] = useState(() => new Map());
  const [savedHuntsCollapsed, setSavedHuntsCollapsed] = useState(true);
  const [bonusHuntMode, setBonusHuntMode] = useState('random');
  const [bonusHuntSearch, setBonusHuntSearch] = useState('');
  const [manualSelectedSlots, setManualSelectedSlots] = useState([]);
  const [addingToCurrentHunt, setAddingToCurrentHunt] = useState(false);
  const [bonusHuntLuckySlot, setBonusHuntLuckySlot] = useState(null);
  const [isBonusHuntLuckySpinning, setIsBonusHuntLuckySpinning] = useState(false);
  const [selectedProviders, setSelectedProviders] = useState(new Set(providers));
  const [providerDropdownOpen, setProviderDropdownOpen] = useState(false);
  const [shuffledSlots, setShuffledSlots] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [maxMinBet, setMaxMinBet] = useState(null);
  const [minRtp, setMinRtp] = useState(null);
  const gridRef = useRef(null);
  const slotsGridRef = useRef(null);
  const [gridLayout, setGridLayout] = useState({ columns: 1, rowSize: 100, columnGap: 10 });
  const providerFilterRef = useRef(null);
  const providerToggleRef = useRef(null);
  const bonusHuntRef = useRef(null);
  const bonusHuntSpinRef = useRef(null);
  const providersRef = useRef(providers);
  const activeAccountIdRef = useRef(null);

  useEffect(() => {
    const grid = slotsGridRef.current;
    if (!grid) return;

    const updateGridLayout = () => {
      const style = getComputedStyle(grid);
      const columnWidths = style.gridTemplateColumns.split(' ').map(parseFloat);
      const columns = columnWidths.length;
      const columnGap = parseFloat(style.columnGap) || 0;
      const rowGap = parseFloat(style.rowGap) || 0;
      const rowSize = (columnWidths[0] * 9) / 16 + rowGap;

      setGridLayout((current) => (
        current.columns === columns &&
        current.columnGap === columnGap &&
        Math.abs(current.rowSize - rowSize) < 0.5
          ? current
          : { columns, rowSize, columnGap }
      ));
    };

    updateGridLayout();
    const observer = new ResizeObserver(updateGridLayout);
    observer.observe(grid);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!showHelp) return undefined;

    const closeOnEscape = (event) => {
      if (event.key === 'Escape') setShowHelp(false);
    };

    window.addEventListener('keydown', closeOnEscape);
    return () => window.removeEventListener('keydown', closeOnEscape);
  }, [showHelp]);

  const showDemoSlot = !isSpinning;
  const gridItemCount = shuffledSlots.length + Number(showDemoSlot);
  const gridRowCount = Math.ceil(gridItemCount / gridLayout.columns);
  const gridVirtualizer = useVirtualizer({
    count: gridRowCount,
    getScrollElement: () => slotsGridRef.current,
    estimateSize: () => gridLayout.rowSize,
    overscan: 3,
  });

  useEffect(() => {
    let cancelled = false;
    fetch(`${import.meta.env.BASE_URL}slot_711_links.json`)
      .then((response) => response.ok ? response.json() : {})
      .then((links) => {
        if (!cancelled) setSlot711LinksByProviderAndName(new Map(Object.entries(links)));
      })
      .catch(() => {});

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!supabase) return undefined;

    let active = true;
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!active) return;
      setAuthUser(session?.user ?? null);
      setAuthReady(true);
      setAuthMessage('');
    });

    supabase.auth.getSession().then(({ data, error }) => {
      if (!active) return;
      if (error) setAuthMessage('Could not check your Google sign-in session.');
      setAuthUser(data?.session?.user ?? null);
      setAuthReady(true);
    });

    return () => {
      active = false;
      subscription.unsubscribe();
    };
  }, []);

  useEffect(() => {
    if (!authReady) return;
    const userId = authUser?.id ?? null;
    const previousUserId = activeAccountIdRef.current;

    if (previousUserId && previousUserId !== userId) {
      const guestState = parseStoredState(
        window.localStorage.getItem(APP_STATE_KEY),
        createDefaultAppState(providersRef.current),
      );
      restoreAppState(guestState, providersRef.current, {
        setSelectedProviders,
        setSearchTerm,
        setMaxMinBet,
        setMinRtp,
        setBonusHuntList,
        setBonusHuntData,
        setActiveBonusHunt,
        setBonusHuntHistory,
        setBonusHuntName,
      });
      setCloudSyncStatus('guest');
    }
    if (previousUserId !== userId) setCloudStateLoadedFor(null);
    activeAccountIdRef.current = userId;
  }, [authReady, authUser?.id]);

  useEffect(() => {
    if (!authReady) return;
    const storageKey = getStateStorageKey(authUser?.id);
    const data = parseStoredState(
      window.localStorage.getItem(storageKey),
      createDefaultAppState(providersRef.current),
    );
    restoreAppState(data, providersRef.current, {
      setSelectedProviders,
      setSearchTerm,
      setMaxMinBet,
      setMinRtp,
      setBonusHuntList,
      setBonusHuntData,
      setActiveBonusHunt,
      setBonusHuntHistory,
      setBonusHuntName,
    });
    setLoadedStorageKey(storageKey);
    setCloudSyncStatus(authUser?.id ? 'loading' : 'guest');
  }, [authReady, authUser?.id]);

  useEffect(() => {
    const userId = authUser?.id;
    if (!supabase || !userId || loadedStorageKey !== getStateStorageKey(userId)) return undefined;
    if (cloudStateLoadedFor === userId) return undefined;

    let cancelled = false;
    const loadAccountState = async () => {
      setCloudSyncStatus('loading');
      const { data, error } = await supabase
        .from('slotselector_user_state')
        .select('state, updated_at')
        .eq('user_id', userId)
        .maybeSingle();

      if (cancelled) return;
      if (error) {
        setCloudSyncStatus('error');
        return;
      }

      const userState = parseStoredState(window.localStorage.getItem(getStateStorageKey(userId)));
      const guestState = parseStoredState(window.localStorage.getItem(APP_STATE_KEY));
      const cloudState = data?.state
        ? { ...data.state, updatedAt: data.state.updatedAt ?? data.updated_at }
        : null;
      const mergedState = mergeAccountState(
        userState,
        guestState,
        cloudState,
        createDefaultAppState(providersRef.current),
      );

      restoreAppState(mergedState, providersRef.current, {
        setSelectedProviders,
        setSearchTerm,
        setMaxMinBet,
        setMinRtp,
        setBonusHuntList,
        setBonusHuntData,
        setActiveBonusHunt,
        setBonusHuntHistory,
        setBonusHuntName,
      });
      setCloudStateLoadedFor(userId);
      setCloudSyncStatus(data ? 'synced' : 'saving');
    };

    loadAccountState();
    return () => {
      cancelled = true;
    };
  }, [authUser?.id, loadedStorageKey, cloudStateLoadedFor]);

  useEffect(() => {
    if (!authReady || loadedStorageKey !== getStateStorageKey(authUser?.id)) return;
    if (authUser?.id && cloudStateLoadedFor !== authUser.id) return;
    const payload = {
      selectedProviders: Array.from(selectedProviders),
      searchTerm,
      maxMinBet,
      minRtp,
      bonusHuntList,
      bonusHuntData,
      activeBonusHunt,
      bonusHuntHistory,
      bonusHuntName,
      updatedAt: new Date().toISOString(),
    };
    window.localStorage.setItem(loadedStorageKey, JSON.stringify(payload));
    setPersistedPayload(payload);
  }, [
    authReady,
    authUser?.id,
    cloudStateLoadedFor,
    loadedStorageKey,
    selectedProviders,
    searchTerm,
    maxMinBet,
    minRtp,
    bonusHuntList,
    bonusHuntData,
    activeBonusHunt,
    bonusHuntHistory,
    bonusHuntName,
  ]);

  useEffect(() => {
    const userId = authUser?.id;
    if (!supabase || !userId || cloudStateLoadedFor !== userId || !persistedPayload) return undefined;

    let cancelled = false;
    const timeout = window.setTimeout(async () => {
      setCloudSyncStatus('saving');
      const { error } = await supabase.from('slotselector_user_state').upsert({
        user_id: userId,
        state: persistedPayload,
        updated_at: persistedPayload.updatedAt,
      }, { onConflict: 'user_id' });

      if (!cancelled) setCloudSyncStatus(error ? 'error' : 'synced');
    }, 500);

    return () => {
      cancelled = true;
      window.clearTimeout(timeout);
    };
  }, [authUser?.id, cloudStateLoadedFor, persistedPayload]);

  const minimumBetOptions = [...new Set(fullSlots
    .map((slot) => slot.minBet)
    .filter(Number.isFinite))]
    .sort((left, right) => left - right);
  const allMinimumBetsIndex = minimumBetOptions.length;
  const selectedMinimumBetIndex = maxMinBet === null
    ? allMinimumBetsIndex
    : Math.max(0, minimumBetOptions.findIndex((amount) => amount >= maxMinBet));
  const minimumRtpOptions = [...new Set(fullSlots
    .map((slot) => slot.rtp)
    .filter(Number.isFinite))]
    .sort((left, right) => left - right);
  const selectedMinimumRtpIndex = minRtp === null
    ? 0
    : Math.min(minimumRtpOptions.length, Math.max(1, minimumRtpOptions.findIndex((value) => value >= minRtp) + 1));

  // Filter slots based on selected providers, search term, stake, and RTP.
  const filteredSlots = fullSlots.filter(slot => 
    selectedProviders.has(slot.provider) && 
    slot.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
    (maxMinBet === null || (Number.isFinite(slot.minBet) && slot.minBet <= maxMinBet)) &&
    (minRtp === null || (Number.isFinite(slot.rtp) && slot.rtp >= minRtp))
  );

  const bonusHuntPickerSlots = filteredSlots.filter(slot => {
    const query = bonusHuntSearch.trim().toLowerCase();
    return !query || `${slot.name} ${slot.provider}`.toLowerCase().includes(query);
  });

  const calculateSlotSpent = (data) => {
    if (!data) return '';
    if (!Object.prototype.hasOwnProperty.call(data, 'stoppingBalance')) return data.spent ?? '';

    const startingBalance = Number.parseFloat(data.startingBalance);
    const stoppingBalance = Number.parseFloat(data.stoppingBalance);
    if (!Number.isFinite(startingBalance) || !Number.isFinite(stoppingBalance)) return '';
    return (startingBalance - stoppingBalance).toFixed(2);
  };
  const formatCurrency = (amount) => `${amount < 0 ? '-€' : '€'}${Math.abs(amount).toFixed(2)}`;
  const bonusHuntSlotRecords = bonusHuntList.map((slot, index) => ({ slot, index }));
  const activeBonusHuntSlots = bonusHuntSlotRecords.filter(({ index }) => !bonusHuntData[index]?.endedWithoutBonus);
  const endedBonusHuntSlots = bonusHuntSlotRecords.filter(({ index }) => bonusHuntData[index]?.endedWithoutBonus);
  const totalSpent = Object.values(bonusHuntData).reduce((sum, data) => {
    const amount = Number.parseFloat(calculateSlotSpent(data));
    return sum + (Number.isFinite(amount) ? amount : 0);
  }, 0);
  const totalPayout = Object.values(bonusHuntData).reduce((sum, data) => sum + (Number.parseFloat(data?.payout) || 0), 0);

  // Shuffle slots only when filters change, not during spinning
  useEffect(() => {
    const newShuffledSlots = [...filteredSlots].sort(() => Math.random() - 0.5);
    setShuffledSlots(newShuffledSlots);
  }, [selectedProviders, searchTerm, maxMinBet, minRtp]);

  useEffect(() => {
    if (!providerDropdownOpen) return undefined;

    const handlePointerDown = (event) => {
      if (!providerFilterRef.current?.contains(event.target)) setProviderDropdownOpen(false);
    };
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setProviderDropdownOpen(false);
        providerToggleRef.current?.focus();
      }
    };

    document.addEventListener('pointerdown', handlePointerDown);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('pointerdown', handlePointerDown);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [providerDropdownOpen]);

  const handleProviderToggle = (provider) => {
    const newProviders = new Set(selectedProviders);
    if (newProviders.has(provider)) {
      newProviders.delete(provider);
    } else {
      newProviders.add(provider);
    }
    setSelectedProviders(newProviders);
  };

  const handleSelectAllProviders = () => setSelectedProviders(new Set(providers));
  const handleClearProviders = () => setSelectedProviders(new Set());

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
    setSpinWinner(winningSlot);
    setSpinId((current) => current + 1);
  };

  const stopBonusHuntPickerSpin = () => {
    if (bonusHuntSpinRef.current !== null) {
      window.clearInterval(bonusHuntSpinRef.current);
      bonusHuntSpinRef.current = null;
    }
    setIsBonusHuntLuckySpinning(false);
  };

  const startBonusHunt = (slots, appendToCurrent = false) => {
    if (!slots.length) return;
    stopBonusHuntPickerSpin();

    const shouldAppend = appendToCurrent && bonusHuntList.length > 0;
    const slotKey = (slot) => slot.image || `${slot.provider}:${slot.name}`;
    const seenSlots = new Set((shouldAppend ? bonusHuntList : []).map(slotKey));
    const uniqueSlots = slots.filter((slot) => {
      const key = slotKey(slot);
      if (seenSlots.has(key)) return false;
      seenSlots.add(key);
      return true;
    });
    const duplicatesSkipped = slots.length - uniqueSlots.length;

    if (!uniqueSlots.length) {
      if (shouldAppend) {
        setBonusHuntAddMessage(duplicatesSkipped === 1
          ? 'That slot is already in the hunt.'
          : 'Those slots are already in the hunt.');
      }
      return;
    }

    const startIndex = shouldAppend ? bonusHuntList.length : 0;
    const nextSlots = shouldAppend ? [...bonusHuntList, ...uniqueSlots] : uniqueSlots;
    const nextData = shouldAppend ? { ...bonusHuntData } : {};
    uniqueSlots.forEach((slot, index) => {
      const { minBet } = getSlotBetLimits(slot);
      nextData[startIndex + index] = {
        startingBalance: '',
        stoppingBalance: '',
        betSize: minBet.toFixed(2),
        payout: '0.00',
        endedWithoutBonus: false,
      };
    });

    setBonusHuntList(nextSlots);
    setBonusHuntData(nextData);
    setActiveBonusHunt(true);
    if (shouldAppend) {
      const addedMessage = `${uniqueSlots.length} ${uniqueSlots.length === 1 ? 'slot' : 'slots'} added to the hunt.`;
      const skippedMessage = duplicatesSkipped
        ? ` ${duplicatesSkipped} already in the hunt and skipped.`
        : '';
      setBonusHuntAddMessage(`${addedMessage}${skippedMessage}`);
    } else {
      setShowBonusHunt(false);
      setAddingToCurrentHunt(false);
      setBonusHuntAddMessage('');
    }

    if (!shouldAppend) {
      const totalBet = Object.values(nextData).reduce((sum, data) => sum + (parseFloat(data.betSize) || 0), 0);
      const entry = {
        id: Date.now(),
        name: bonusHuntName?.trim() || 'Untitled Hunt',
        createdAt: new Date().toISOString(),
        slots: nextSlots,
        data: nextData,
        totalBet,
        totalSpent: 0,
        totalPayout: 0,
      };
      setBonusHuntHistory((prev) => [entry, ...prev].slice(0, 50));
    }
  };

  const generateBonusHunt = () => {
    const count = Math.min(Math.max(bonusHuntCount, 1), filteredSlots.length);
    const selected = [];
    const available = [...filteredSlots];

    while (selected.length < count) {
      const randomIndex = Math.floor(Math.random() * available.length);
      selected.push(available.splice(randomIndex, 1)[0]);
    }

    startBonusHunt(selected, addingToCurrentHunt);
  };

  const openBonusHuntCreator = (appendToCurrent = false, mode = 'random') => {
    stopBonusHuntPickerSpin();
    setBonusHuntMode(mode);
    setBonusHuntSearch('');
    setManualSelectedSlots([]);
    setBonusHuntLuckySlot(null);
    setBonusHuntAddMessage('');
    setAddingToCurrentHunt(appendToCurrent);
    setShowBonusHunt(true);
  };

  const closeBonusHuntCreator = () => {
    stopBonusHuntPickerSpin();
    setShowBonusHunt(false);
  };

  const addManualSelection = () => {
    startBonusHunt(manualSelectedSlots, addingToCurrentHunt);
    setManualSelectedSlots([]);
  };

  const toggleManualSlot = (slot) => {
    setManualSelectedSlots((current) =>
      current.some((selected) => selected.image === slot.image)
        ? current.filter((selected) => selected.image !== slot.image)
        : [...current, slot]
    );
  };

  const spinBonusHuntPicker = () => {
    if (isBonusHuntLuckySpinning || !filteredSlots.length) return;

    let cycles = 0;
    setIsBonusHuntLuckySpinning(true);
    bonusHuntSpinRef.current = window.setInterval(() => {
      const randomIndex = Math.floor(Math.random() * filteredSlots.length);
      setBonusHuntLuckySlot(filteredSlots[randomIndex]);
      cycles += 1;
      if (cycles >= 24) stopBonusHuntPickerSpin();
    }, 100);
  };

  const addLuckyPickerSelection = () => {
    if (!bonusHuntLuckySlot || isBonusHuntLuckySpinning) return;
    startBonusHunt([bonusHuntLuckySlot], addingToCurrentHunt);
    setBonusHuntLuckySlot(null);
  };

  const addLuckyPickToBonusHunt = () => {
    if (!selectedSlot) return;
    startBonusHunt([selectedSlot], bonusHuntList.length > 0);
    setSelectedSlot(null);
  };

  const updateBetSize = (index, value) => {
    setBonusHuntData((current) => ({
      ...current,
      [index]: { ...current[index], betSize: value },
    }));
  };

  const updateSlotMoney = (index, field, value) => {
    setBonusHuntData((current) => ({
      ...current,
      [index]: { ...current[index], [field]: value },
    }));
  };

  const normalizeSlotMoney = (index, field) => {
    const value = bonusHuntData[index]?.[field] ?? '';
    if (!value.trim()) return;
    const amount = Number.parseFloat(value);
    updateSlotMoney(index, field, Number.isFinite(amount) ? Math.max(0, amount).toFixed(2) : '');
  };

  const endSlotWithoutBonus = (index) => {
    setBonusHuntData((current) => ({
      ...current,
      [index]: {
        ...current[index],
        endedWithoutBonus: true,
      },
    }));
  };

  const restoreSlotToHunt = (index) => {
    setBonusHuntData((current) => ({
      ...current,
      [index]: { ...current[index], endedWithoutBonus: false },
    }));
  };

  const stepBetSize = (index, cents) => {
    const { minBet, maxBet } = getSlotBetLimits(bonusHuntList[index] ?? {});
    const currentAmount = Number.parseFloat(bonusHuntData[index]?.betSize);
    const amount = Number.isFinite(currentAmount) ? currentAmount : minBet;
    const nextAmount = Math.min(maxBet, Math.max(minBet, amount + cents / 100));
    updateBetSize(index, nextAmount.toFixed(2));
  };

  const normalizeBetSize = (index) => {
    const { minBet, maxBet } = getSlotBetLimits(bonusHuntList[index] ?? {});
    const currentAmount = Number.parseFloat(bonusHuntData[index]?.betSize);
    const normalizedValue = Number.isFinite(currentAmount)
      ? Math.min(maxBet, Math.max(minBet, currentAmount)).toFixed(2)
      : minBet.toFixed(2);
    updateBetSize(index, normalizedValue);
  };

  const handleGoogleSignIn = async () => {
    if (!supabase) return;
    setAuthBusy(true);
    setAuthMessage('');
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin },
    });
    if (error) {
      setAuthMessage('Google sign-in could not be started. Please try again.');
      setAuthBusy(false);
    }
  };

  const handleSignOut = async () => {
    if (!supabase) return;
    setAuthBusy(true);
    const { error } = await supabase.auth.signOut();
    setAuthMessage(error ? 'Could not sign out. Please try again.' : '');
    setAuthBusy(false);
  };

  const saveCurrentBonusHunt = () => {
    if (!bonusHuntList.length) return;
    const name = bonusHuntName?.trim() || 'Untitled Hunt';
    const normalizedName = name.toLowerCase();
    const alreadySaved = bonusHuntHistory.some((entry) =>
      entry.name?.trim().toLowerCase() === normalizedName
    );
    if (alreadySaved) {
      setBonusHuntSaveMessage({
        type: 'error',
        text: `A saved hunt named "${name}" already exists.`,
      });
      return;
    }

    const totalBet = Object.values(bonusHuntData).reduce((sum, data) => sum + (parseFloat(data?.betSize) || 0), 0);
    const savedTotalPayout = Object.values(bonusHuntData).reduce((sum, data) => sum + (parseFloat(data?.payout) || 0), 0);
    const entry = {
      id: Date.now(),
      name,
      createdAt: new Date().toISOString(),
      slots: bonusHuntList,
      data: bonusHuntData,
      totalBet,
      totalSpent,
      totalPayout: savedTotalPayout,
    };
    setBonusHuntHistory((prev) => [entry, ...prev].slice(0, 50));
    setBonusHuntSaveMessage({ type: 'success', text: `Saved "${name}".` });
  };

  const loadBonusHunt = (entry) => {
    if (!entry) return;
    const slots = entry.slots || [];
    setBonusHuntList(slots);
    setBonusHuntData(ensureBonusHuntBetSizes(slots, entry.data));
    setBonusHuntName(entry.name || '');
    setBonusHuntSaveMessage(null);
    setActiveBonusHunt(true);
    setShowBonusHunt(false);
  };

  const deleteBonusHunt = (id) => {
    setBonusHuntHistory((prev) => prev.filter((entry) => entry.id !== id));
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
              setActiveBonusHunt(null);
              setShowBonusHunt(false);
              setTimeout(() => {
                if (gridRef.current) {
                  gridRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
              }, 0);
            }}
          >
            Slots
          </button>
          <button
            className="nav-btn"
            onClick={() => {
              setShowBonusHunt(false);
              setActiveBonusHunt(true);
            }}
          >
            Bonus Hunt
          </button>
          <button className="nav-btn" type="button" onClick={() => setShowHelp(true)}>
            Help
          </button>
          <button
            className="nav-bonus-btn"
            onClick={() => openBonusHuntCreator()}
          >
            ➕ Create Bonus Hunt
          </button>
          {supabase && (
            <div className="account-controls">
              {!authReady ? (
                <span className="account-status">Checking account...</span>
              ) : authUser ? (
                <>
                  <span className="account-email" title={authUser.email}>{authUser.email || 'Signed in'}</span>
                  <span className={`account-status ${cloudSyncStatus}`} role="status">
                    {cloudSyncStatus === 'error' ? 'Cloud sync paused' : cloudSyncStatus === 'synced' ? 'Synced' : 'Syncing...'}
                  </span>
                  <button className="account-button" type="button" onClick={handleSignOut} disabled={authBusy}>
                    Sign out
                  </button>
                </>
              ) : (
                <button className="account-button google-signin-button" type="button" onClick={handleGoogleSignIn} disabled={authBusy}>
                  {authBusy ? 'Opening Google...' : 'Sign in with Google'}
                </button>
              )}
              {authMessage && <span className="account-error" role="alert">{authMessage}</span>}
            </div>
          )}
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
            <div className="bonus-hunt-header-actions">
              <button
                className="bonus-hunt-page-add-btn"
                type="button"
                onClick={() => openBonusHuntCreator(true, 'manual')}
              >
                + Add Slots
              </button>
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
          </div>

          <div className="bonus-hunt-page-content">
            {bonusHuntList.length === 0 ? (
              <div className="bonus-hunt-empty">
                <p>No bonus hunt yet. Generate one to get started.</p>
                <button
                  className="bonus-hunt-generate-btn"
                  type="button"
                  onClick={() => openBonusHuntCreator()}
                >
                  Create Bonus Hunt
                </button>
              </div>
            ) : (
              <div className="bonus-hunt-list">
                {activeBonusHuntSlots.length > 0 ? (
                  <>
                    <div className="bonus-hunt-list-header">
                      <span className="col col-idx">#</span>
                      <span className="col col-game">Game</span>
                      <span className="col col-start-balance">Starting Balance</span>
                      <span className="col col-stop-balance">Stopping Balance</span>
                      <span className="col col-bet">Bet Size</span>
                      <span className="col col-spent">Spent</span>
                      <span className="col col-payout">Payout</span>
                      <span className="col col-actions">Status</span>
                    </div>
                    {activeBonusHuntSlots.map(({ slot, index }) => {
                      const { minBet, maxBet } = getSlotBetLimits(slot);
                      const rtp = getSlotRtp(slot);
                      return (
                      <div key={index} className="bonus-hunt-row">
                        <span className="col col-idx">{index + 1}</span>
                        <div className="col col-game">
                          <BonusHuntThumbnail slot={slot} />
                          <div className="slot-game-info">
                            <span className="slot-title">{slot.name}</span>
                            <span className="slot-provider">{slot.provider}</span>
                            {rtp != null && <span className="slot-rtp">RTP {rtp}%</span>}
                            {getSlotCasinoLinks(slot, slot711LinksByProviderAndName).map(({ casino, url }) => (
                              <a key={casino} className="slot-casino-link" href={url} target="_blank" rel="noopener noreferrer">
                                Open on {casino}
                              </a>
                            ))}
                          </div>
                        </div>
                        <div className="col col-start-balance">
                          <span className="field-label">Starting Balance</span>
                          <div className="input-wrapper">
                            <span className="currency">€</span>
                            <input
                              type="text"
                              inputMode="decimal"
                              value={bonusHuntData[index]?.startingBalance ?? ''}
                              onChange={(event) => updateSlotMoney(index, 'startingBalance', event.target.value)}
                              onBlur={() => normalizeSlotMoney(index, 'startingBalance')}
                              aria-label={`Starting balance for ${slot.name}`}
                              className="page-input-field"
                            />
                          </div>
                        </div>
                        <div className="col col-stop-balance">
                          <span className="field-label">Stopping Balance</span>
                          <div className="input-wrapper">
                            <span className="currency">€</span>
                            <input
                              type="text"
                              inputMode="decimal"
                              value={bonusHuntData[index]?.stoppingBalance ?? ''}
                              onChange={(event) => updateSlotMoney(index, 'stoppingBalance', event.target.value)}
                              onBlur={() => normalizeSlotMoney(index, 'stoppingBalance')}
                              aria-label={`Stopping balance for ${slot.name}`}
                              className="page-input-field"
                            />
                          </div>
                        </div>
                        <div className="col col-bet">
                          <span className="field-label">Bet Size</span>
                          <div className="input-wrapper">
                            <span className="currency">€</span>
                            <input
                              type="text"
                              inputMode="decimal"
                              value={bonusHuntData[index]?.betSize ?? minBet.toFixed(2)}
                              onChange={(event) => updateBetSize(index, event.target.value)}
                              onBlur={() => normalizeBetSize(index)}
                              aria-label={`Bet size for ${slot.name}`}
                              className="page-input-field bet-size-input"
                            />
                            <div className="bet-stepper">
                              <button
                                type="button"
                                className="bet-step-button"
                                onClick={() => stepBetSize(index, 10)}
                                disabled={(Number.parseFloat(bonusHuntData[index]?.betSize) || minBet) >= maxBet}
                                aria-label={`Increase bet for ${slot.name} by €0.10`}
                                title="Increase by €0.10"
                              >+</button>
                              <button
                                type="button"
                                className="bet-step-button"
                                onClick={() => stepBetSize(index, -10)}
                                disabled={(Number.parseFloat(bonusHuntData[index]?.betSize) || minBet) <= minBet}
                                aria-label={`Decrease bet for ${slot.name} by €0.10`}
                                title="Decrease by €0.10"
                              >−</button>
                            </div>
                          </div>
                        </div>
                        <div className="col col-spent">
                          <span className="field-label">Spent</span>
                          <div className="input-wrapper">
                            <span className="currency">€</span>
                            <input
                              type="text"
                              value={calculateSlotSpent(bonusHuntData[index])}
                              readOnly
                              aria-label={`Calculated spend for ${slot.name}`}
                              className="page-input-field computed-money-input"
                            />
                          </div>
                        </div>
                        <div className="col col-payout">
                          <span className="field-label">Payout</span>
                          <div className="input-wrapper">
                            <span className="currency">€</span>
                            <input
                              type="number"
                              step="0.01"
                              min="0"
                              value={bonusHuntData[index]?.payout || '0.00'}
                              onChange={(event) => setBonusHuntData({
                                ...bonusHuntData,
                                [index]: { ...bonusHuntData[index], payout: event.target.value }
                              })}
                              aria-label={`Payout for ${slot.name}`}
                              className="page-input-field"
                            />
                          </div>
                        </div>
                        <div className="col col-actions">
                          <button
                            type="button"
                            className="slot-no-bonus-btn"
                            onClick={() => endSlotWithoutBonus(index)}
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                      );
                    })}
                  </>
                ) : (
                  <p className="bonus-hunt-no-active">No active slots. Add a slot or restore one from the ended list.</p>
                )}

                {endedBonusHuntSlots.length > 0 && (
                  <section className="bonus-hunt-ended">
                    <div className="bonus-hunt-ended-header">
                      <h3>Ended Without Bonus</h3>
                      <span>{endedBonusHuntSlots.length} session{endedBonusHuntSlots.length === 1 ? '' : 's'}</span>
                    </div>
                    {endedBonusHuntSlots.map(({ slot, index }) => (
                      <div key={index} className="bonus-hunt-ended-row">
                        <div className="bonus-hunt-ended-slot">
                          <img src={slot.image} alt={slot.name} />
                          <div>
                            <strong>{slot.name}</strong>
                            <span>{slot.provider}</span>
                          </div>
                        </div>
                        <div className="bonus-hunt-ended-value">
                          <span>Starting Balance</span>
                          <strong>
                            {Number.isFinite(Number.parseFloat(bonusHuntData[index]?.startingBalance))
                              ? formatCurrency(Number.parseFloat(bonusHuntData[index].startingBalance))
                              : 'Not recorded'}
                          </strong>
                        </div>
                        <div className="bonus-hunt-ended-value">
                          <span>Stopping Balance</span>
                          <strong>
                            {Number.isFinite(Number.parseFloat(bonusHuntData[index]?.stoppingBalance))
                              ? formatCurrency(Number.parseFloat(bonusHuntData[index].stoppingBalance))
                              : 'Not recorded'}
                          </strong>
                        </div>
                        <div className="bonus-hunt-ended-value">
                          <span>Spent</span>
                          <strong>
                            {Number.isFinite(Number.parseFloat(calculateSlotSpent(bonusHuntData[index])))
                              ? formatCurrency(Number.parseFloat(calculateSlotSpent(bonusHuntData[index])))
                              : 'Not recorded'}
                          </strong>
                        </div>
                        <button type="button" className="slot-restore-btn" onClick={() => restoreSlotToHunt(index)}>
                          Restore
                        </button>
                      </div>
                    ))}
                  </section>
                )}
              </div>
            )}

            <div className="bonus-hunt-page-summary">
              <div className="summary-card">
                <div className="summary-item">
                  <span className="summary-label">Total Slots</span>
                  <span className="summary-value">{bonusHuntList.length}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Active Slots</span>
                  <span className="summary-value">{activeBonusHuntSlots.length}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Total Spent</span>
                  <span className="summary-value">{formatCurrency(totalSpent)}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Total Payout</span>
                  <span className="summary-value">€{totalPayout.toFixed(2)}</span>
                </div>
              </div>

              <div className="bonus-hunt-save">
                <input
                  type="text"
                  value={bonusHuntName}
                  onChange={(e) => {
                    setBonusHuntName(e.target.value);
                    setBonusHuntSaveMessage(null);
                  }}
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
              {bonusHuntSaveMessage && (
                <p className={`bonus-hunt-save-message ${bonusHuntSaveMessage.type}`} role="status">
                  {bonusHuntSaveMessage.text}
                </p>
              )}
              <p className="bonus-hunt-storage-notice" role="note">
                {authUser
                  ? cloudSyncStatus === 'error'
                    ? 'Cloud sync is unavailable. Existing browser data is still saved, but changes may not sync until you reconnect.'
                    : 'Your signed-in hunts sync to your account, with a local copy kept in this browser.'
                  : 'Guest hunts are saved in this browser on this device. They are not synced to an account, and clearing this site’s data can remove them.'}
              </p>

              {bonusHuntHistory.length > 0 && (
                <div className="saved-hunts">
                  <div className="saved-hunts-header">
                    <div className="saved-hunts-title">
                      <h4>Saved Hunts</h4>
                      <span>{bonusHuntHistory.length} saved</span>
                    </div>
                    <button
                      className="toggle-saved-hunts-btn"
                      onClick={() => setSavedHuntsCollapsed((v) => !v)}
                    >
                      {savedHuntsCollapsed ? 'Show' : 'Hide'}
                    </button>
                  </div>
                  {!savedHuntsCollapsed && (
                    <div className="saved-hunts-list">
                      {bonusHuntHistory.slice(0, 6).map((entry) => (
                        <div key={entry.id} className="saved-hunt-card">
                          <div className="saved-hunt-info">
                            <div className="saved-hunt-meta">
                              <div className="saved-hunt-name">{entry.name}</div>
                              <div className="saved-hunt-sub">{new Date(entry.createdAt).toLocaleString()}</div>
                            </div>
                            <div className="saved-hunt-stats">
                              <span>{entry.slots?.length || 0} slots</span>
                              <span>Spent €{Number(entry.totalSpent ?? entry.totalBet ?? 0).toFixed(2)}</span>
                            </div>
                          </div>
                          <div className="saved-hunt-actions">
                            <button className="load-hunt-btn" onClick={() => loadBonusHunt(entry)}>
                              Load
                            </button>
                            <button className="delete-hunt-btn" onClick={() => deleteBonusHunt(entry.id)}>
                              Delete
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

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
            <div className="provider-header">
              <h3>Providers</h3>
            </div>
            <div className="min-bet-filter">
              <div className="min-bet-filter-heading">
                <label htmlFor="max-min-bet">Maximum minimum bet</label>
                <output htmlFor="max-min-bet">
                  {maxMinBet === null ? 'All' : `\u20ac${formatStakeValue(maxMinBet)}`}
                </output>
              </div>
              <input
                id="max-min-bet"
                type="range"
                min="0"
                max={allMinimumBetsIndex}
                step="1"
                value={selectedMinimumBetIndex}
                aria-label="Maximum minimum bet"
                aria-valuetext={maxMinBet === null ? 'All minimum bets' : `\u20ac${formatStakeValue(maxMinBet)} maximum minimum bet`}
                onChange={(event) => {
                  const index = Number(event.target.value);
                  setMaxMinBet(index === allMinimumBetsIndex ? null : minimumBetOptions[index]);
                }}
              />
              <div className="min-bet-filter-scale">
                <span>{'\u20ac'}{formatStakeValue(minimumBetOptions[0] ?? 0)}</span>
                <span>All</span>
              </div>
            </div>
            <div className="min-rtp-filter">
              <div className="min-rtp-filter-heading">
                <label htmlFor="min-rtp">Minimum RTP</label>
                <output htmlFor="min-rtp">
                  {minRtp === null ? 'All' : formatRtpValue(minRtp)}
                </output>
              </div>
              <input
                id="min-rtp"
                type="range"
                min="0"
                max={minimumRtpOptions.length}
                step="1"
                value={selectedMinimumRtpIndex}
                aria-label="Minimum RTP"
                aria-valuetext={minRtp === null ? 'All RTP values' : `${formatRtpValue(minRtp)} minimum RTP`}
                onChange={(event) => {
                  const index = Number(event.target.value);
                  setMinRtp(index === 0 ? null : minimumRtpOptions[index - 1]);
                }}
              />
              <div className="min-rtp-filter-scale">
                <span>All</span>
                <span>{formatRtpValue(minimumRtpOptions.at(-1) ?? 0)}</span>
              </div>
            </div>
            <div className="provider-selector" ref={providerFilterRef}>
              <button
                ref={providerToggleRef}
                type="button"
                className="provider-dropdown-toggle"
                aria-expanded={providerDropdownOpen}
                aria-controls="provider-selector-menu"
                onClick={() => setProviderDropdownOpen((open) => !open)}
              >
                <span>Game providers</span>
                <span className="provider-dropdown-selection">
                  {selectedProviders.size === providers.length ? 'All selected' : `${selectedProviders.size} selected`}
                </span>
                <span className="provider-dropdown-chevron" aria-hidden="true" />
              </button>
              {providerDropdownOpen && (
                <div id="provider-selector-menu" className="provider-selector-menu" role="group" aria-label="Filter by provider">
                  <div className="provider-selector-menu-header">
                    <span>Filter by provider</span>
                    <span>{selectedProviders.size}/{providers.length}</span>
                  </div>
                  <div className="provider-selector-actions">
                    <button type="button" onClick={handleSelectAllProviders}>Select All</button>
                    <button type="button" onClick={handleClearProviders}>Clear</button>
                  </div>
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
              )}
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
          <div className="grid-container" ref={slotsGridRef}>
            <div className="virtual-grid-spacer" style={{ height: gridVirtualizer.getTotalSize() }}>
              {gridVirtualizer.getVirtualItems().map((virtualRow) => {
                const firstItemIndex = virtualRow.index * gridLayout.columns;
                const rowItemCount = Math.min(gridLayout.columns, gridItemCount - firstItemIndex);

                return (
                  <div
                    key={virtualRow.key}
                    className="virtual-grid-row"
                    style={{
                      transform: `translateY(${virtualRow.start}px)`,
                      gridTemplateColumns: `repeat(${gridLayout.columns}, minmax(0, 1fr))`,
                      columnGap: `${gridLayout.columnGap}px`,
                    }}
                  >
                    {Array.from({ length: rowItemCount }, (_, columnIndex) => {
                      const itemIndex = firstItemIndex + columnIndex;
                      if (showDemoSlot && itemIndex === 0) {
                        return (
                          <div key="demo" className="grid-item demo-item">
                            <div className="demo-content">
                              <div className="demo-text">🎰</div>
                            </div>
                          </div>
                        );
                      }

                      const slotIndex = itemIndex - Number(showDemoSlot);
                      const slot = shuffledSlots[slotIndex];
                      const [casinoLink] = getSlotCasinoLinks(slot, slot711LinksByProviderAndName);

                      return (
                        <div key={`${slot.provider}-${slot.name}-${slotIndex}`} className="grid-item" data-provider={slot.provider}>
                          {casinoLink ? (
                            <>
                              <a
                                className="grid-slot-play-link"
                                href={casinoLink.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                aria-label={`Play ${slot.name} on ${casinoLink.casino}`}
                                title={`Play on ${casinoLink.casino}`}
                              >
                                <img src={slot.image} alt={slot.name} loading="lazy" decoding="async" fetchPriority="low" />
                              </a>
                              <span className="grid-slot-play-hint" aria-hidden="true">Play on {casinoLink.casino}</span>
                            </>
                          ) : (
                            <img src={slot.image} alt={slot.name} loading="lazy" decoding="async" fetchPriority="low" />
                          )}
                          <div className="grid-item-label">
                            <span className="slot-name">{slot.name}</span>
                            <span className="slot-provider">{slot.provider}</span>
                            <div className="slot-metadata">
                              <div className="slot-stakes">
                                <span>Min {Number.isFinite(slot.minBet) ? `\u20ac${formatStakeValue(slot.minBet)}` : '\u2014'}</span>
                                <span>Max {Number.isFinite(slot.maxBet) ? `\u20ac${formatStakeValue(slot.maxBet)}` : '\u2014'}</span>
                              </div>
                              <span>RTP {formatRtpValue(slot.rtp)}</span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
        
        <div className="right-panel">
          <div className="button-container">
            <LuckyPickReel
              initialSlots={fullSlots.slice(0, REEL_SLOT_COUNT)}
              slots={filteredSlots}
              winningSlot={spinWinner}
              spinId={spinId}
              isSpinning={isSpinning}
              onFinish={(winner) => {
                setSelectedSlot(winner);
                setIsSpinning(false);
              }}
            />
            <button className="spin-button" onClick={spin} disabled={isSpinning || filteredSlots.length === 0}>
              <span className={`spin-icon ${isSpinning ? 'spinning' : ''}`}>✨</span>
              <span>Lucky<br/>Pick</span>
            </button>
          </div>
        </div>

        {selectedSlot && (
          <div className="modal-overlay" onClick={() => setSelectedSlot(null)}>
            <div className="modal-content lucky-modal" onClick={(e) => e.stopPropagation()}>
              <div className="lucky-modal-header">
                <span className="lucky-badge">✨ Lucky Pick</span>
                <button className="lucky-close" onClick={() => setSelectedSlot(null)}>
                  Close
                </button>
              </div>
              <div className="lucky-modal-body">
                <div className="lucky-image-wrap">
                  <img src={selectedSlot.image} alt={selectedSlot.name} />
                </div>
                <div className="lucky-details">
                  <h3 className="lucky-title">{selectedSlot.name}</h3>
                  <p className="lucky-provider">{selectedSlot.provider}</p>
                  <p className="lucky-min-bet">
                    Min bet {Number.isFinite(selectedSlot.minBet) ? `\u20ac${formatStakeValue(selectedSlot.minBet)}` : '\u2014'}
                  </p>
                  {getSlotRtp(selectedSlot) != null && (
                    <p className="lucky-rtp">RTP {getSlotRtp(selectedSlot)}%</p>
                  )}
                  {getSlotCasinoLinks(selectedSlot, slot711LinksByProviderAndName).map(({ casino, url }) => (
                    <a key={casino} className="slot-casino-link" href={url} target="_blank" rel="noopener noreferrer">
                      Open on {casino}
                    </a>
                  ))}
                  <p className="lucky-sub">Add it to your next bonus hunt or spin again.</p>
                </div>
              </div>
              <div className="lucky-actions">
                <button className="lucky-btn ghost" onClick={() => {
                  setSelectedSlot(null);
                  setTimeout(() => spin(), 50);
                }}>Spin Again</button>
                <button
                  className="lucky-btn solid"
                  onClick={addLuckyPickToBonusHunt}
                >
                  ➕ Add to Bonus Hunt
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
      )}

      {showHelp && (
        <div className="modal-overlay help-overlay" onClick={() => setShowHelp(false)}>
          <section
            className="modal-content help-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="help-title"
            onClick={(event) => event.stopPropagation()}
          >
            <header className="help-modal-header">
              <div>
                <span className="help-eyebrow">Quick guide</span>
                <h2 id="help-title">Using SlotSelector</h2>
              </div>
              <button type="button" className="help-close-btn" autoFocus onClick={() => setShowHelp(false)}>
                Close
              </button>
            </header>

            <div className="help-guide-grid">
              <section>
                <h3>Find a slot</h3>
                <ul>
                  <li>Search by game title. Choose providers from the provider menu.</li>
                  <li>Set the highest allowed minimum bet and the lowest RTP with the sliders.</li>
                  <li>The Showing count and slot grid update to match your filters.</li>
                </ul>
              </section>
              <section>
                <h3>Play or pick</h3>
                <ul>
                  <li>Cards marked “Play on 711” open that game at 711 in a new tab; not every game has a verified link.</li>
                  <li>Lucky Pick draws from the slots matching your current filters. Spin Again draws another pick.</li>
                  <li>Use Add to Bonus Hunt on a pick to add it to a hunt.</li>
                </ul>
              </section>
              <section>
                <h3>Create a Bonus Hunt</h3>
                <ul>
                  <li>Choose Slots to search and select games, Random Slots to draw a chosen number, or Lucky Pick to spin for one game.</li>
                  <li>All three modes use your current provider and slot filters.</li>
                  <li>Use Add Slots on an active hunt to add more games.</li>
                </ul>
              </section>
              <section>
                <h3>Track and save</h3>
                <ul>
                  <li>Enter starting and stopping balances, bet sizes, and payouts for each game. Spent and hunt totals update from your entries.</li>
                  <li>Name a hunt and choose Save Hunt. Load or delete saved hunts from the Saved Hunts list.</li>
                  <li>Your filters and hunt data are stored in this browser and are not shared across devices.</li>
                </ul>
              </section>
            </div>
          </section>
        </div>
      )}

      {showBonusHunt && (
        <div className="modal-overlay" onClick={closeBonusHuntCreator}>
          <div className="modal-content bonus-hunt-modal" onClick={(e) => e.stopPropagation()}>
            <h2>{addingToCurrentHunt ? 'Add Slots to Bonus Hunt' : 'Create Bonus Hunt'}</h2>
            {bonusHuntAddMessage && <p className="bonus-hunt-hint" role="status">{bonusHuntAddMessage}</p>}
            <div className="bonus-hunt-mode-switch" role="group" aria-label="Slot selection mode">
              <button
                type="button"
                className={`bonus-hunt-mode-button ${bonusHuntMode === 'manual' ? 'active' : ''}`}
                aria-pressed={bonusHuntMode === 'manual'}
                onClick={() => {
                  stopBonusHuntPickerSpin();
                  setBonusHuntMode('manual');
                }}
              >
                Choose Slots
              </button>
              <button
                type="button"
                className={`bonus-hunt-mode-button ${bonusHuntMode === 'random' ? 'active' : ''}`}
                aria-pressed={bonusHuntMode === 'random'}
                onClick={() => {
                  stopBonusHuntPickerSpin();
                  setBonusHuntMode('random');
                }}
              >
                Random Slots
              </button>
              <button
                type="button"
                className={`bonus-hunt-mode-button ${bonusHuntMode === 'lucky' ? 'active' : ''}`}
                aria-pressed={bonusHuntMode === 'lucky'}
                onClick={() => {
                  stopBonusHuntPickerSpin();
                  setBonusHuntMode('lucky');
                }}
              >
                Lucky Pick
              </button>
            </div>
            {bonusHuntMode === 'random' ? (
              <>
                <p className="bonus-hunt-description">
                  {addingToCurrentHunt ? 'How many random slots should be added?' : 'How many random slots should the hunt include?'}
                </p>
                <div className="bonus-hunt-input-group">
                  <input
                    type="number"
                    min="1"
                    max={filteredSlots.length}
                    value={bonusHuntCount}
                    onChange={(e) => setBonusHuntCount(Math.max(1, parseInt(e.target.value) || 1))}
                    className="bonus-hunt-input"
                  />
                  <button className="bonus-hunt-generate-btn" onClick={generateBonusHunt} disabled={!filteredSlots.length}>
                    {addingToCurrentHunt ? 'Add Random Slots' : 'Start Random Hunt'}
                  </button>
                </div>
                <p className="bonus-hunt-hint">Choose from {filteredSlots.length} slots matching your provider filters and search.</p>
              </>
            ) : bonusHuntMode === 'manual' ? (
              <>
                <input
                  type="search"
                  className="bonus-hunt-slot-search"
                  placeholder="Search slots or providers..."
                  aria-label="Search slots or providers"
                  value={bonusHuntSearch}
                  onChange={(event) => setBonusHuntSearch(event.target.value)}
                />
                <div className="bonus-hunt-slot-picker">
                  {bonusHuntPickerSlots.slice(0, 100).map((slot) => {
                    const isSelected = manualSelectedSlots.some((selected) => selected.image === slot.image);
                    return (
                      <label key={slot.image} className={`bonus-hunt-slot-option ${isSelected ? 'selected' : ''}`}>
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleManualSlot(slot)}
                        />
                        <img src={slot.image} alt="" loading="lazy" />
                        <span>
                          <strong>{slot.name}</strong>
                          <small>{slot.provider}</small>
                        </span>
                      </label>
                    );
                  })}
                  {bonusHuntPickerSlots.length === 0 && <p className="bonus-hunt-no-results">No filtered slots match that search.</p>}
                </div>
                <p className="bonus-hunt-hint">
                  {manualSelectedSlots.length} selected
                  {bonusHuntPickerSlots.length > 100 ? ' · Showing the first 100 matches; narrow your search to find more.' : ''}
                </p>
                <button
                  className="bonus-hunt-manual-submit"
                  type="button"
                  onClick={addManualSelection}
                  disabled={!manualSelectedSlots.length}
                >
                  {manualSelectedSlots.length
                    ? `${addingToCurrentHunt ? 'Add' : 'Start'} Hunt with ${manualSelectedSlots.length} ${manualSelectedSlots.length === 1 ? 'Slot' : 'Slots'}`
                    : addingToCurrentHunt ? 'Select slots to add' : 'Select slots to start hunt'}
                </button>
              </>
            ) : (
              <div className="bonus-hunt-lucky-content">
                <p className="bonus-hunt-description">
                  Spin until you find a slot you want to add to this hunt.
                </p>
                <div className={`bonus-hunt-lucky-preview ${isBonusHuntLuckySpinning ? 'spinning' : ''}`}>
                  {bonusHuntLuckySlot ? (
                    <>
                      <img src={bonusHuntLuckySlot.image} alt={bonusHuntLuckySlot.name} />
                      <div>
                        <strong>{bonusHuntLuckySlot.name}</strong>
                        <small>{bonusHuntLuckySlot.provider}</small>
                        <div className="bonus-hunt-lucky-stats">
                          <span>Bet size {'\u20ac'}{formatStakeValue(getSlotBetLimits(bonusHuntLuckySlot).minBet)}</span>
                          {getSlotRtp(bonusHuntLuckySlot) != null && (
                            <span>RTP {getSlotRtp(bonusHuntLuckySlot)}%</span>
                          )}
                        </div>
                        {getSlotCasinoLinks(bonusHuntLuckySlot, slot711LinksByProviderAndName).map(({ casino, url }) => (
                          <a key={casino} className="slot-casino-link" href={url} target="_blank" rel="noopener noreferrer">
                            Open on {casino}
                          </a>
                        ))}
                      </div>
                    </>
                  ) : (
                    <span>Your pick will appear here</span>
                  )}
                </div>
                <div className="bonus-hunt-lucky-actions">
                  <button
                    className="bonus-hunt-lucky-spin"
                    type="button"
                    onClick={spinBonusHuntPicker}
                    disabled={isBonusHuntLuckySpinning || !filteredSlots.length}
                  >
                    {isBonusHuntLuckySpinning ? 'Spinning...' : 'Spin Lucky Pick'}
                  </button>
                  <button
                    className="bonus-hunt-lucky-add"
                    type="button"
                    onClick={addLuckyPickerSelection}
                    disabled={!bonusHuntLuckySlot || isBonusHuntLuckySpinning}
                  >
                    {addingToCurrentHunt ? 'Add to Hunt' : 'Start Hunt with This Slot'}
                  </button>
                </div>
                <p className="bonus-hunt-hint">Uses the slots currently visible under your provider filters and search.</p>
              </div>
            )}
            <button className="close-bonus-hunt-btn" onClick={closeBonusHuntCreator}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
