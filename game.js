const followerCountEl = document.getElementById('follower-count');
const loveCountEl = document.getElementById('love-count');
const faveCountEl = document.getElementById('fave-count');
const profileTitleEl = document.getElementById('profile-title');
const profileImageEl = document.getElementById('profile-image');
const profileLinkEl = document.getElementById('profile-link');
const bioTextEl = document.getElementById('bio-text');

const UNICODE_LETTER_MAP = {
  'ᴀ': 'a', 'ʙ': 'b', 'ᴄ': 'c', 'ᴅ': 'd', 'ᴇ': 'e', 'ꜰ': 'f', 'ɢ': 'g', 'ʜ': 'h', 'ɪ': 'i',
  'ᴋ': 'k', 'ʟ': 'l', 'ᴍ': 'm', 'ɴ': 'n', 'ᴏ': 'o', 'ᴘ': 'p', 'ʀ': 'r', 'ꜛ': 's', 'ꜜ': 's',
  'ꜝ': 's', 'ꜞ': 's', 'ꜟ': 'f', 'ᴛ': 't', 'ᴜ': 'u', 'ᴠ': 'v', 'ᴡ': 'w', 'ʏ': 'y', 'ᴢ': 'z'
};

function formatNumber(value) {
  return Number(value || 0).toLocaleString();
}

function normalizeProfileText(text = '') {
  return Array.from(text)
    .map((char) => UNICODE_LETTER_MAP[char] ?? char)
    .join('')
    .replace(/\u202f/g, ' ')
    .replace(/\xa0/g, ' ')
    .toLowerCase();
}

function extractCountFromBio(bioText, label) {
  const normalized = normalizeProfileText(bioText);
  const pattern = new RegExp(`${label}\\s*[:\\-]?\\s*([0-9][0-9\\s,]*)`, 'i');
  const match = normalized.match(pattern);

  if (!match) return null;

  const cleanValue = match[1].replace(/[,\s]/g, '').split('/')[0].split('k')[0];
  const parsed = Number(cleanValue);
  return Number.isFinite(parsed) ? parsed : null;
}

async function loadScratchUser(username) {
  const safeUsername = (username || 'yoshihome').trim();

  try {
    const response = await fetch(`/api/user?username=${encodeURIComponent(safeUsername)}`);
    if (!response.ok) throw new Error('User not found');

    const user = await response.json();
    const profile = user.profile || {};
    const bioText = user.bio || profile.bio || 'No bio available.';

    const followers = Number(user.followers ?? extractCountFromBio(bioText, 'followers') ?? 0);
    const loves = Number(user.loves ?? extractCountFromBio(bioText, 'loves') ?? 0);
    const faves = Number(user.faves ?? extractCountFromBio(bioText, 'faves') ?? 0);

    if (profileTitleEl) {
      profileTitleEl.textContent = user.username || safeUsername;
    }

    if (profileImageEl) {
      const avatar = profile.images?.['90x90'] || profile.images?.['55x55'] || '';
      profileImageEl.src = avatar || 'yoshihome pfp.png';
      profileImageEl.alt = `${user.username || safeUsername} profile picture`;
    }

    if (profileLinkEl) {
      const scratchUrl = `https://scratch.mit.edu/users/${encodeURIComponent(user.username || safeUsername)}/`;
      profileLinkEl.href = scratchUrl;
      profileLinkEl.setAttribute('aria-label', `Open ${user.username || safeUsername} on Scratch`);
    }

    if (bioTextEl) {
      bioTextEl.textContent = bioText;
    }

    if (followerCountEl) followerCountEl.textContent = formatNumber(followers);
    if (loveCountEl) loveCountEl.textContent = formatNumber(loves);
    if (faveCountEl) faveCountEl.textContent = formatNumber(faves);

    return user;
  } catch (error) {
    console.warn('Could not load Scratch user:', error);

    if (profileTitleEl) profileTitleEl.textContent = safeUsername;
    if (profileLinkEl) profileLinkEl.href = `https://scratch.mit.edu/users/${encodeURIComponent(safeUsername)}/`;
    if (bioTextEl) bioTextEl.textContent = 'This Scratch user could not be loaded.';
    if (followerCountEl) followerCountEl.textContent = '0';
    if (loveCountEl) loveCountEl.textContent = '0';
    if (faveCountEl) faveCountEl.textContent = '0';

    return null;
  }
}

async function loadStats() {
  const fallbackStats = {
    followers: followerCountEl?.dataset.fallback || '18,370',
    loves: loveCountEl?.dataset.fallback || '178,442',
    faves: faveCountEl?.dataset.fallback || '163,214'
  };

  try {
    const response = await fetch(`stats.json?v=${Date.now()}`);
    if (!response.ok) throw new Error('stats.json not available');

    const stats = await response.json();

    if (followerCountEl) {
      followerCountEl.textContent = formatNumber(stats.followers ?? fallbackStats.followers.replace(/,/g, ''));
    }

    if (loveCountEl) {
      loveCountEl.textContent = formatNumber(stats.loves ?? fallbackStats.loves.replace(/,/g, ''));
    }

    if (faveCountEl) {
      faveCountEl.textContent = formatNumber(stats.faves ?? fallbackStats.faves.replace(/,/g, ''));
    }
  } catch (error) {
    console.warn('Could not load stats.json:', error);

    if (followerCountEl) followerCountEl.textContent = fallbackStats.followers;
    if (loveCountEl) loveCountEl.textContent = fallbackStats.loves;
    if (faveCountEl) faveCountEl.textContent = fallbackStats.faves;
  }
}

function getProjectIdFromItem(item) {
  return item.dataset.projectId || null;
}

async function loadProjectViews() {
  const projectItems = document.querySelectorAll('.project-item');

  try {
    const response = await fetch(`project_views.json?v=${Date.now()}`);
    if (!response.ok) throw new Error('project_views.json not available');

    const projectViews = await response.json();

    for (const item of projectItems) {
      const projectId = getProjectIdFromItem(item);
      const statsEl = item.querySelector('.project-1-stats, .project-2-stats, .project-3-stats, .project-4-stats');

      if (!projectId || !statsEl) continue;

      const views = projectViews[projectId];

      if (typeof views === 'number') {
        statsEl.textContent = `${formatNumber(views)} views`;
      }
    }
  } catch (error) {
    console.warn('Could not load project_views.json:', error);
  }
}

function bindHomeSearch() {
  const form = document.getElementById('scratch-search-form');
  const input = document.getElementById('scratch-search-input');

  if (!form || !input) return;

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const username = input.value.trim();

    if (!username) return;
    window.location.href = `userpage.html?username=${encodeURIComponent(username)}`;
  });
}

function initializePage() {
  const params = new URLSearchParams(window.location.search);
  const username = params.get('username');

  bindHomeSearch();

  if (username) {
    loadScratchUser(username);
    return;
  }

  loadStats();
  loadProjectViews();
  setInterval(loadStats, 60000);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializePage);
} else {
  initializePage();
}
