// Blog data
const blogs = [
  {
    title: "Why Most People Are Blind to Their Own Potential",
    desc: "The biggest tragedy in life is not death—it's what dies inside of us while we're still alive.",
    meta: "⭐ May 14 · 11.2K Reads · 331 Comments",
    img: "https://picsum.photos/300/200?random=1",
    category: "Psychology"
  },
  {
    title: "The Art of Saying No: A Guide to Setting Boundaries",
    desc: "Learn how to say no without feeling guilty and set healthy boundaries in your life.",
    meta: "⭐ Aug 10 · 5.4K Reads · 198 Comments",
    img: "https://picsum.photos/300/200?random=4",
    category: "Psychology"
  },
  {
    title: "The Science of Happiness: What Really Makes Us Happy",  
    desc: "Explore the latest research on happiness and how to apply it to your life.",
    meta: "⭐ Oct 12 · 7.8K Reads · 312 Comments",
    img: "https://picsum.photos/300/200?random=6",
    category: "Psychology"
  },
  {
    title: "If You Write A Book, Don't Tell Anyone",
    desc: "Learn from my regret; stay silent.",
    meta: "⭐ Jun 17 · 6.5K Reads · 286 Comments",
    img: "https://picsum.photos/300/200?random=2",
    category: "Writing"
  },
  {
    title: "How to Build a Successful Side Hustle from Scratch",  
    desc: "Step-by-step guide to starting and growing a profitable side hustle.",
    meta: "⭐ Nov 3 · 10.1K Reads · 289 Comments",
    img: "https://picsum.photos/300/200?random=7",
    category: "Writing"
  },
  {
    title: "3 Remote Sites Paying $1,500/Day You've Never Heard Of",
    desc: "These hidden gems can boost your income significantly.", 
    meta: "⭐ Jul 22 · 8.1K Reads · 412 Comments",  
    img: "https://picsum.photos/300/200?random=3",
    category: "Productivity"
  },
  { 
    title: "10 Productivity Hacks That Actually Work",
    desc: "Boost your productivity with these scientifically proven hacks.",
    meta: "⭐ Sep 5 · 9.3K Reads · 256 Comments",
    img: "https://picsum.photos/300/200?random=5",
    category: "Productivity"    
  },
  {
    title: "The Ultimate Guide to Remote Work: Tips and Tools for Success",  
    desc: "Everything you need to know to thrive in a remote work environment.",
    meta: "⭐ Dec 15 · 6.9K Reads · 234 Comments",
    img: "https://picsum.photos/300/200?random=8",
    category: "Productivity"
  }
];

// --- added: sample stories data for Stories page ---
const publishedStories = [
  { title: "Nostalgia.", date: "Published 12h ago", read: "3 min read", views: 0, comments: 0 },
  { title: "Halki si mohobbat!", date: "Published 4d ago", read: "3 min read", views: 21, comments: 0 },
  { title: "Intezaar", date: "Published 4d ago", read: "2 min read", views: 1, comments: 0 },
  { title: "Itna single hoon.", date: "Published Nov 7", read: "3 min read", views: 5, comments: 0 }
];

const unlistedStories = []; // keep empty to show empty state
const submissionItems = []; // keep empty to show submissions empty state

// Helper: ensure a safe inner wrapper for each tab so we don't overwrite sibling content
function ensureTabInner(id) {
  let container = document.getElementById(id);
  if (!container) return null;
  let inner = container.querySelector('.tab-inner');
  if (!inner) {
    inner = document.createElement('div');
    inner.className = 'tab-inner';
    // keep any existing markup (e.g. draft items) separate by appending inner, not replacing container
    container.appendChild(inner);
  }
  return inner;
}

// Render Published list (layout like image 1)
function renderPublished() {
  const inner = ensureTabInner('published-content');
  if (!inner) return;

  const header = `
    <div class="published-list-header">
      <div class="col-latest">Latest</div>
      <div class="col-publication">Publication</div>
      <div class="col-status">Status</div>
    </div>
  `;

  const listItems = publishedStories.map(st => `
    <div class="published-row">
      <div class="thumb">
        <div class="thumb-placeholder"></div>
      </div>
      <div class="published-info">
        <h4 class="published-title">${st.title}</h4>
        <div class="published-meta">${st.date} • ${st.read}</div>
        <div class="published-stats">
          <span class="stat-eye">👁 ${st.views}</span>
          <span class="stat-comment">💬 ${st.comments}</span>
        </div>
      </div>
      <div class="published-actions">...</div>
    </div>
  `).join('');

  inner.innerHTML = `
    ${header}
    <div class="published-list">${listItems}</div>
  `;
}

// Render Unlisted empty state (image 2)
function renderUnlisted() {
  const inner = ensureTabInner('unlisted-content');
  if (!inner) return;

  if (unlistedStories.length === 0) {
    inner.innerHTML = `
      <div class="empty-state-box">
        <p>No unlisted stories yet.</p>
      </div>
    `;
  } else {
    const list = unlistedStories.map(st => `
      <div class="published-row">
        <div class="thumb"><div class="thumb-placeholder"></div></div>
        <div class="published-info">
          <h4 class="published-title">${st.title}</h4>
          <div class="published-meta">${st.date} • ${st.read}</div>
        </div>
        <div class="published-actions">...</div>
      </div>
    `).join('');
    inner.innerHTML = `<div class="published-list">${list}</div>`;
  }
}

// Render Submissions empty state (image 3)
function renderSubmissions() {
  const inner = ensureTabInner('submissions-content');
  if (!inner) return;

  if (submissionItems.length === 0) {
    inner.innerHTML = `
      <div class="empty-state-box">
        <p>You have no submissions yet.</p>
        <a href="#" class="explore-publications-link">Explore publications</a>
      </div>
    `;
  } else {
    const list = submissionItems.map(s => `
      <div class="published-row">
        <div class="published-info">
          <h4 class="published-title">${s.title}</h4>
          <div class="published-meta">${s.date} • ${s.read}</div>
        </div>
        <div class="published-actions">...</div>
      </div>
    `).join('');
    inner.innerHTML = `<div class="published-list">${list}</div>`;
  }
}

// Render category-based articles
function renderCategoryArticles() {
  // Psychology articles
  const psychologyGrid = document.querySelector('.psychology .cards-grid');
  if (psychologyGrid) {
    const psychologyArticles = blogs.filter(blog => blog.category === 'Psychology');
    psychologyGrid.innerHTML = '';
    psychologyArticles.forEach(article => {
      const card = createCard(article);
      psychologyGrid.appendChild(card);
    });
  }

  // Writing articles
  const writingGrid = document.querySelector('.writing .cards-grid');
  if (writingGrid) {
    const writingArticles = blogs.filter(blog => blog.category === 'Writing');
    writingGrid.innerHTML = '';
    writingArticles.forEach(article => {
      const card = createCard(article);
      writingGrid.appendChild(card);
    });
  }

  // Productivity articles
  const productivityGrid = document.querySelector('.productivity .cards-grid');
  if (productivityGrid) {
    const productivityArticles = blogs.filter(blog => blog.category === 'Productivity');
    productivityGrid.innerHTML = '';
    productivityArticles.forEach(article => {
      const card = createCard(article);
      productivityGrid.appendChild(card);
    });
  }
}

// Create card element
function createCard(article) {
  const card = document.createElement('div');
  card.className = 'card';
  card.innerHTML = `
    <img src="${article.img}" alt="${article.title}" class="card-image">
    <div class="card-content">
      <h3>${article.title}</h3>
      <p>${article.desc}</p>
      <div class="meta">
        <span>${article.meta}</span>
      </div>
    </div>
  `;
  return card;
}

// Chart functionality
function initChart() {
  const canvas = document.getElementById('analyticsChart');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  
  // Sample data for the chart
  const data = {
    labels: ['Oct 1', 'Oct 8', 'Oct 15', 'Oct 22', 'Oct 29'],
    datasets: [
      {
        label: 'Views',
        data: [5, 8, 12, 15, 7],
        borderColor: '#1a8917',
        backgroundColor: 'rgba(26, 137, 23, 0.1)',
        tension: 0.4
      },
      {
        label: 'Reads', 
        data: [2, 3, 5, 7, 3],
        borderColor: '#0066cc',
        backgroundColor: 'rgba(0, 102, 204, 0.1)',
        tension: 0.4
      }
    ]
  };

  drawChart(ctx, data);
}

function drawChart(ctx, data) {
  const canvas = ctx.canvas;
  const width = canvas.width;
  const height = canvas.height;
  
  // Clear canvas
  ctx.clearRect(0, 0, width, height);
  
  // Chart dimensions
  const padding = 60;
  const chartWidth = width - 2 * padding;
  const chartHeight = height - 2 * padding;
  
  // Find max value for scaling
  const allValues = data.datasets.flatMap(dataset => dataset.data);
  const maxValue = Math.max(...allValues);
  const scale = chartHeight / maxValue;
  
  // Draw grid lines
  ctx.strokeStyle = '#e0e0e0';
  ctx.lineWidth = 1;
  
  // Horizontal grid lines
  for (let i = 0; i <= 5; i++) {
    const y = padding + (chartHeight / 5) * i;
    ctx.beginPath();
    ctx.moveTo(padding, y);
    ctx.lineTo(width - padding, y);
    ctx.stroke();
  }
  
  // Vertical grid lines
  const stepX = chartWidth / (data.labels.length - 1);
  for (let i = 0; i < data.labels.length; i++) {
    const x = padding + stepX * i;
    ctx.beginPath();
    ctx.moveTo(x, padding);
    ctx.lineTo(x, height - padding);
    ctx.stroke();
  }
  
  // Draw datasets
  data.datasets.forEach((dataset, datasetIndex) => {
    ctx.strokeStyle = dataset.borderColor;
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    dataset.data.forEach((value, index) => {
      const x = padding + stepX * index;
      const y = height - padding - (value * scale);
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    
    ctx.stroke();
    
    // Draw points
    ctx.fillStyle = dataset.borderColor;
    dataset.data.forEach((value, index) => {
      const x = padding + stepX * index;
      const y = height - padding - (value * scale);
      
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, 2 * Math.PI);
      ctx.fill();
    });
  });
  
  // Draw labels
  ctx.fillStyle = '#666';
  ctx.font = '12px Inter';
  ctx.textAlign = 'center';
  
  data.labels.forEach((label, index) => {
    const x = padding + stepX * index;
    ctx.fillText(label, x, height - padding + 20);
  });
}

// Global variables for page management
let currentPage = 'homePage';

// Hide all pages function
function hideAllPages() {
  const allPages = document.querySelectorAll('.profile-section, .stats-section, .stories-section, .library-section, .collaborate-section, .register-section, .write-section');
  allPages.forEach(page => {
    page.classList.add('hidden');
  });
  
  const feed = document.querySelector('.feed');
  const rightPanel = document.querySelector('.right-panel');
  if (feed) feed.style.display = 'none';
  if (rightPanel) rightPanel.style.display = 'none';
}

// Show specific page function
function showPage(pageId) {
  hideAllPages();
  currentPage = pageId;
  
  if (pageId === 'homePage') {
    const feed = document.querySelector('.feed');
    const rightPanel = document.querySelector('.right-panel');
    if (feed) feed.style.display = 'block';
    if (rightPanel) rightPanel.style.display = 'block';
  } else {
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
      targetPage.classList.remove('hidden');
    }
  }
}

// Show home function
function showHome() {
  showPage('homePage');
  updateActiveNavItem('homePage');
}

// Update active navigation item
function updateActiveNavItem(activePageId) {
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.classList.remove('active');
    if (item.dataset.page === activePageId) {
      item.classList.add('active');
    }
  });
}

// Write page functionality
function openWritePage() {
  hideAllPages();
  const writePage = document.getElementById('writePage');
  if (writePage) {
    writePage.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    
    // Focus on title input
    setTimeout(() => {
      const titleInput = document.getElementById('storyTitle');
      if (titleInput) titleInput.focus();
    }, 100);
  }
}

function closeWritePage() {
  const writePage = document.getElementById('writePage');
  if (writePage) {
    writePage.classList.add('hidden');
    document.body.style.overflow = 'auto';
    showHome();
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log('Initializing BlogZ application...');
  
  // Initialize blog articles and chart
  renderCategoryArticles();
  initChart();
  
  // Get all menu button elements - ADD ALL THE MENU BUTTONS
  const menuButtons = [
    document.getElementById('menuBtn'),              // Home page
    document.getElementById('menuBtnLibrary'),       // Library page  
    document.getElementById('menuBtnProfile'),       // Profile page
    document.getElementById('menuBtnStories'),       // Stories page
    document.getElementById('menuBtnStats'),         // Stats page
    document.getElementById('menuBtnCollaborate'),   // Collaborate page
    document.getElementById('menuBtnRegister')       // Register page
  ];

  const sidebar = document.getElementById('sidebar');
  const navItems = document.querySelectorAll('.nav-item');

  // Check if sidebar exists
  if (!sidebar) {
    console.error('Sidebar not found!');
    return;
  }

  // Toggle sidebar function
  function toggleSidebar() {
    console.log('Toggling sidebar...');
    sidebar.classList.toggle('sidebar-visible');
    document.body.classList.toggle('sidebar-open');
  }

  // Add event listeners to ALL menu buttons
  menuButtons.forEach((button) => {
    if (button) {
      console.log(`Found menu button: ${button.id}`);
      button.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log(`Menu button clicked: ${this.id}`);
        toggleSidebar();
      });
    } else {
      console.log('Menu button not found');
    }
  });

  // Navigation items event listeners
  navItems.forEach(item => {
    item.addEventListener('click', function(e) {
      e.preventDefault();
      const pageId = this.dataset.page;
      console.log('Navigating to:', pageId);
      
      showPage(pageId);
      updateActiveNavItem(pageId);
      
      // Close sidebar after navigation
      sidebar.classList.remove('sidebar-visible');
      document.body.classList.remove('sidebar-open');
    });
  });

  // Close sidebar when clicking outside
  document.addEventListener('click', function(e) {
    const isMenuButton = e.target.closest('.menu-btn');
    const isInsideSidebar = sidebar.contains(e.target);
    
    if (!isMenuButton && !isInsideSidebar && sidebar.classList.contains('sidebar-visible')) {
      sidebar.classList.remove('sidebar-visible');
      document.body.classList.remove('sidebar-open');
    }
  });

  // Universal Back-to-Home handler (applies to all .back-to-home buttons)
  document.querySelectorAll('.back-to-home').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      // show home page using existing helpers
      if (typeof showPage === 'function') showPage('homePage');
      if (typeof updateActiveNavItem === 'function') updateActiveNavItem('homePage');

      // close sidebar if open
      const sidebar = document.getElementById('sidebar');
      if (sidebar) {
        sidebar.classList.remove('sidebar-visible');
        document.body.classList.remove('sidebar-open');
      }

      // reset scroll and focus
      window.scrollTo(0, 0);
    });
  });

  // Theme toggle functionality for all pages
  const themeButtons = [
    document.getElementById('themeToggle'),
    document.getElementById('themeToggleLibrary'),
    document.getElementById('themeToggleProfile'),
    document.getElementById('themeToggleStories'),
    document.getElementById('themeToggleStats'),
    document.getElementById('themeToggleCollaborate'),
    document.getElementById('themeToggleRegister')
  ];

  themeButtons.forEach(button => {
    if (button) {
      button.addEventListener('click', function() {
        const body = document.body;
        const currentTheme = body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Update all theme toggle icons
        themeButtons.forEach(btn => {
          if (btn) {
            const icon = btn.querySelector('.material-icons');
            if (icon) {
              icon.textContent = newTheme === 'dark' ? 'dark_mode' : 'light_mode';
            }
          }
        });
      });
    }
  });

  // Load saved theme
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.body.setAttribute('data-theme', savedTheme);
  themeButtons.forEach(button => {
    if (button) {
      const icon = button.querySelector('.material-icons');
      if (icon) {
        icon.textContent = savedTheme === 'dark' ? 'dark_mode' : 'light_mode';
      }
    }
  });

  // Stories tab switching (Drafts / Published / Unlisted / Submissions)
  const storyTabs = document.querySelectorAll('.stories-tab');
  const tabContents = document.querySelectorAll('.tab-content');

  function showStoriesTab(tabName) {
    // tabName values: 'drafts' | 'published' | 'unlisted' | 'submissions'
    // deactivate all tabs
    storyTabs.forEach(t => t.classList.remove('active'));
    // hide all contents
    tabContents.forEach(c => c.classList.remove('active'));

    // activate clicked tab
    const clickedTab = document.querySelector(`.stories-tab[data-tab="${tabName}"]`);
    if (clickedTab) clickedTab.classList.add('active');

    // show corresponding content
    const contentEl = document.getElementById(`${tabName}-content`);
    if (contentEl) contentEl.classList.add('active');

    // render content for the selected tab (only update that tab's inner wrapper)
    if (tabName === 'published') {
      renderPublished();
    } else if (tabName === 'unlisted') {
      renderUnlisted();
    } else if (tabName === 'submissions') {
      renderSubmissions();
    }

    // scroll to content top (optional)
    const storiesMain = document.querySelector('.stories-main-content');
    if (storiesMain) storiesMain.scrollTop = 0;
  }

  // attach listeners
  storyTabs.forEach(tab => {
    tab.addEventListener('click', function(e) {
      e.preventDefault();
      const target = this.dataset.tab;
      if (!target) return;
      showStoriesTab(target);
    });
  });

  // ensure default tab is shown (matches HTML initial state)
  const initialTab = document.querySelector('.stories-tab.active')?.dataset.tab || 'drafts';
  showStoriesTab(initialTab);

  // Initialize - show home page by default
  showPage('homePage');
  updateActiveNavItem('homePage');

  console.log('BlogZ application initialized successfully');
});

document.addEventListener('DOMContentLoaded', function () {
  // safe selector lookup for the Drafts tab container
  function getDraftsContainer() {
    return document.getElementById('drafts-content')
      || document.querySelector('.drafts-content')
      || document.querySelector('[data-tab-content="drafts"]')
      || document.querySelector('#drafts')
      || document.querySelector('.tab-content.drafts');
  }

  function clearDraftsContent() {
    const drafts = getDraftsContainer();
    if (!drafts) return;
    const inner = drafts.querySelector('.tab-inner');
    if (inner) inner.innerHTML = '';     // clear inner wrapper if present
    else drafts.innerHTML = '';          // otherwise clear whole container
  }

  // Run once on load to remove accidental content
  clearDraftsContent();

  // If you have a global showStoriesTab(tabName) function, ensure Drafts is not overwritten
  if (typeof window.showStoriesTab === 'function') {
    const original = window.showStoriesTab;
    window.showStoriesTab = function(tabName) {
      // clear drafts whenever switching to any other tab
      if (tabName !== 'drafts') clearDraftsContent();
      return original(tabName);
    };
  }

  // Optional: expose for debugging
  window._clearDraftsContent = clearDraftsContent;
});
