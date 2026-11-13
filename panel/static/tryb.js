// Tryb pracy strony. W repozytorium: zwykły panel (dane z API serwera).
// Eksporter lustra tylko-do-odczytu (bc/statyczny.py) podmienia ten plik na wersję z `window.BC_STATYCZNY = true`,
// a wtedy wspolne/api.js czyta pliki dane/<klucz>.json zamiast pytać serwer.
window.BC_STATYCZNY = window.BC_STATYCZNY === true;
