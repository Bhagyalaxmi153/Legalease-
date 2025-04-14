function storeLanguagePreference() {
    const languageSelect = document.querySelector('#google_translate_element select');
    languageSelect.addEventListener('change', () => {
        const selectedLanguage = languageSelect.value;
        localStorage.setItem('preferredLanguage', selectedLanguage);
    });
}
window.addEventListener('load', storeLanguagePreference);


function applySavedLanguage() {
    const savedLanguage = localStorage.getItem('preferredLanguage');
    if (savedLanguage) {
        const languageSelect = document.querySelector('#google_translate_element select');
        if (languageSelect) {
            languageSelect.value = savedLanguage;
            languageSelect.dispatchEvent(new Event('change'));
        }
    }
}
window.addEventListener('load', applySavedLanguage);
