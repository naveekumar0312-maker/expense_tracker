document.addEventListener('DOMContentLoaded', function(){
  const msgs = document.getElementById('messages');
  if (msgs) setTimeout(()=> msgs.style.display='none', 3500);
});