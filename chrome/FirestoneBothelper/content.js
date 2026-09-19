function crazygames() {
  const errmessage = document.querySelectorAll("div[jsname='RH7zg']"); 
  if (errmessage.length) {
    //
  }
}

if (document.location.href.match(/crazygames/)) {
  // Declutter screen
  document.querySelectorAll("div[class^=GamePageDesktop_rightSidebar__]").forEach(el=>el.remove())
  document.querySelectorAll("div[class^=GamePageDesktop_leaderboardContainer__]").forEach(el=>el.remove())
  document.querySelectorAll("div[class^=GameInfo_rightColumn__]").forEach(el=>el.remove())
  document.querySelectorAll("div[class^=GameInfo_leaderboard__]").forEach(el=>el.remove())

  // Go fullscreen
  document.querySelectorAll("button[data-testid='footer-fullscreen-button']").forEach(el=>el.click())
  document.querySelectorAll("button[data-testid='footer-hide-button']").forEach(el=>el.click())

  // Start monitoring
  const observer = new MutationObserver(crazygames);
}

if (typeof observer != 'undefined') {
  observer.observe(document.body, { childList: true, subtree: true });
}