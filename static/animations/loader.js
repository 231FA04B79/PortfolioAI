/* ==========================================================================
   PortfolioAI Core Loader & Interaction Controller
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  
  // --- 1. Global Page Loader Logic ---
  const globalLoader = document.getElementById('global-page-loader');
  const progressBar = document.getElementById('loader-progress-bar');
  const statusText = document.getElementById('loader-status-text');
  
  if (globalLoader && progressBar) {
    let progress = 0;
    const intervalTime = 12; // Speed of loader simulation
    
    const statusMessages = {
      10: 'Initializing secure environment...',
      30: 'Connecting to database channels...',
      55: 'Synthesizing AI score predictors...',
      80: 'Optimizing visual representations...',
      95: 'Finalizing setup...'
    };

    const loaderInterval = setInterval(() => {
      progress += Math.floor(Math.random() * 4) + 1;
      
      if (progress >= 100) {
        progress = 100;
        clearInterval(loaderInterval);
        progressBar.style.width = '100%';
        if (statusText) statusText.textContent = 'Welcome to PortfolioAI!';
        
        // Graceful fadeout transition
        setTimeout(() => {
          globalLoader.classList.add('opacity-0', 'pointer-events-none');
          // Fully remove from DOM tree after transition
          setTimeout(() => {
            globalLoader.remove();
          }, 500);
          
          // Trigger skeletons transition
          document.querySelectorAll('.skeleton-container').forEach(container => {
            container.classList.add('loaded');
          });
        }, 300);
      } else {
        progressBar.style.width = progress + '%';
        
        // Update status subtext if matching benchmark
        Object.keys(statusMessages).forEach(key => {
          if (progress >= parseInt(key)) {
            statusText.textContent = statusMessages[key];
          }
        });
      }
    }, intervalTime);
  } else {
    // If no page loader element (fallback), immediately activate skeletons
    document.querySelectorAll('.skeleton-container').forEach(container => {
      container.classList.add('loaded');
    });
  }

  // --- 2. Button Ripple Effects ---
  document.addEventListener('click', function(e) {
    const btn = e.target.closest('.btn-primary, .btn-secondary, .btn-ripple, .btn');
    if (!btn) return;
    
    // Add ripple wrapper class
    btn.classList.add('btn-ripple-container');
    
    const circle = document.createElement('span');
    const dialog = btn.getBoundingClientRect();
    const d = Math.max(dialog.width, dialog.height);
    
    circle.style.width = circle.style.height = d + 'px';
    circle.style.left = e.clientX - dialog.left - d/2 + 'px';
    circle.style.top = e.clientY - dialog.top - d/2 + 'px';
    circle.classList.add('ripple-effect');
    
    // Remove any previous active ripples
    const prevRipple = btn.querySelector('.ripple-effect');
    if (prevRipple) prevRipple.remove();
    
    btn.appendChild(circle);
  });

  // --- 3. Global Form Submission Interceptor ---
  const textMappings = {
    'login': 'Signing In...',
    'sign in': 'Signing In...',
    'register': 'Registering...',
    'sign up': 'Registering...',
    'save': 'Saving changes...',
    'submit': 'Saving changes...',
    'add': 'Saving changes...',
    'upload': 'Uploading resume file...',
    'analyze': 'Running AI analysis...',
    'generate': 'Synthesizing layout...',
    'create': 'Creating component...',
    'search': 'Filtering records...',
    'delete': 'Permanently deleting...',
    'verify': 'Verifying code...'
  };

  document.addEventListener('submit', function(e) {
    const form = e.target;
    // Skip if marked to ignore loading overlay
    if (form.classList.contains('no-loader')) return;
    
    // Find the submit button
    const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
    const formOverlay = document.getElementById('form-submit-loader');
    const mainWrapper = document.querySelector('main');
    
    // Show submission loader overlay
    if (formOverlay) {
      formOverlay.classList.remove('hidden');
      formOverlay.offsetWidth; // Force layout calculation
      formOverlay.classList.remove('opacity-0');
      formOverlay.classList.add('opacity-100', 'flex');
    }
    
    // Apply blur to layout content
    if (mainWrapper) {
      mainWrapper.classList.add('blur-content');
    }
    
    if (submitBtn) {
      // Disable duplicate clicks
      submitBtn.disabled = true;
      submitBtn.classList.add('cursor-not-allowed', 'opacity-75');
      
      // Attempt to map button text
      let originalText = submitBtn.textContent || submitBtn.value || '';
      originalText = originalText.trim().toLowerCase();
      
      let newText = 'Processing Request...';
      for (const [key, val] of Object.entries(textMappings)) {
        if (originalText.includes(key)) {
          newText = val;
          break;
        }
      }
      
      // Update loading text on submission form spinner if present
      const overlayText = document.getElementById('form-loader-text');
      if (overlayText) {
        overlayText.textContent = newText;
      }
      
      // If text-based button, prepend a spinner inside
      if (submitBtn.tagName === 'BUTTON') {
        submitBtn.innerHTML = `<span class="animate-spin inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full mr-2"></span> ${newText}`;
      }
    }
  });

  // --- 4. Interactive Toast Notification Helper ---
  window.showToast = function(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium shadow-lg border pointer-events-auto transform translate-y-4 opacity-0 transition-all duration-300 max-w-sm w-full bg-white z-[99999]`;
    
    // Apply boundary styles depending on type
    let borderTheme = 'border-emerald-100 text-emerald-800 shadow-emerald-500/5';
    let iconHTML = `<i class="bi bi-check-circle-fill text-emerald-500 text-base"></i>`;
    
    if (type === 'error' || type === 'danger') {
      borderTheme = 'border-rose-100 text-rose-800 shadow-rose-500/5';
      iconHTML = `<i class="bi bi-exclamation-octagon-fill text-rose-500 text-base"></i>`;
    } else if (type === 'warning') {
      borderTheme = 'border-amber-100 text-amber-800 shadow-amber-500/5';
      iconHTML = `<i class="bi bi-exclamation-triangle-fill text-amber-500 text-base"></i>`;
    } else if (type === 'info') {
      borderTheme = 'border-blue-100 text-blue-800 shadow-blue-500/5';
      iconHTML = `<i class="bi bi-info-circle-fill text-blue-500 text-base"></i>`;
    }
    
    toast.className += ` ${borderTheme}`;
    toast.innerHTML = `
      ${iconHTML}
      <div class="flex-grow">${message}</div>
      <button class="text-slate-400 hover:text-slate-650 transition-colors" onclick="this.parentElement.remove()">
        <i class="bi bi-x-lg text-xs"></i>
      </button>
    `;
    
    container.appendChild(toast);
    
    // Trigger transition entry
    setTimeout(() => {
      toast.classList.remove('translate-y-4', 'opacity-0');
    }, 10);
    
    // Auto remove after 5.5 seconds
    setTimeout(() => {
      toast.classList.add('opacity-0', 'scale-95');
      setTimeout(() => {
        toast.remove();
      }, 300);
    }, 5500);
  };
});
