document.addEventListener('DOMContentLoaded', function () {
  // Highlight active sidebar links
  const currentPath = window.location.pathname;
  const sidebarLinks = document.querySelectorAll('.sidebar-link');
  
  sidebarLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href) {
      // Check for exact match or if the current path starts with the link's path (for sub-routes)
      const isExactMatch = currentPath === href;
      const isSubRouteMatch = href !== '/' && href !== '/dashboard/' && currentPath.startsWith(href);
      
      if (isExactMatch || isSubRouteMatch) {
        link.classList.add('active');
        
        // Ensure parent categories/collapse menus are visible if any (for future nested menus)
        let parentCollapse = link.closest('.collapse');
        if (parentCollapse && typeof bootstrap !== 'undefined') {
          const bsCollapse = bootstrap.Collapse.getOrCreateInstance(parentCollapse);
          bsCollapse.show();
        }
      }
    }
  });

  // Smooth delay fade-in for list cards
  const cards = document.querySelectorAll('.card');
  cards.forEach((card, index) => {
    card.style.animationDelay = `${index * 0.05}s`;
    card.classList.add('slide-up');
  });
});
