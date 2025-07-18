// AI Guessing Game - Frontend JavaScript

// Translation dictionary
const translations = {
    en: {
        // Header and navigation
        leaderboard: "Leaderboard",
        my_stats: "My Stats",

        // Welcome screen
        welcome_title: "Welcome to the AI Guessing Game!",
        welcome_description: "Test your knowledge across multiple categories. Get facts one by one and guess the answer. The fewer facts you need, the higher your score!",
        your_name: "Your Name",
        enter_your_name: "Enter your name",
        choose_category: "Choose Category",
        choose_category_optional: "Choose Category (Optional)",
        random_category: "🎲 Random Category",
        loading_categories: "Loading categories...",
        difficulty_level: "Difficulty Level",
        loading_difficulties: "Loading difficulties...",
        language: "Language",
        start_game: "Start Game",

        // Game screen
        category: "Category",
        round_score: "Round Score",
        total_score: "Total Score",
        facts_revealed: "Facts Revealed",
        click_get_hint: "Click \"Get Hint\" to reveal your first fact!",
        get_hint: "Get Hint",
        get_letter_hint: "Get Letter Hint",
        whats_your_guess: "What's your guess?",
        type_your_answer: "Type your answer here...",
        submit: "Submit",
        new_round: "New Round",
        give_up: "Give Up",
        main_menu: "Main Menu",
        
        // Hint system
        letter_hint: "Letter Hint",
        hints_used: "Hints Used",
        hints_remaining: "Hints Remaining",
        letter_revealed: "Letter revealed!",
        no_hints_left: "No hints left for this round",
        no_more_letters: "No more letters to reveal",

        // Result modal
        congratulations: "Congratulations!",
        correct_answer: "Correct!",
        wrong_answer: "Wrong Answer",
        time_up: "Time's Up!",
        you_got_it_right: "You got it right!",
        better_luck_next_time: "Better luck next time!",
        answer: "Answer",
        time_taken: "Time Taken",
        facts_used: "Facts Used",
        play_again: "Play Again",
        change_player: "Change Player",

        // Modals
        global_leaderboard: "Global Leaderboard",
        player_statistics: "Player Statistics",
        loading_leaderboard: "Loading leaderboard...",
        loading_statistics: "Loading statistics...",

        // Messages and notifications
        welcome_message: "Welcome to the AI Guessing Game!",
        connection_lost: "Connection lost. Please refresh the page.",
        fact_revealed_msg: "New fact revealed!",
        correct_guess_msg: "Correct! Well done!",
        incorrect_guess_msg: "Not quite right. Try again!",
        no_more_facts_msg: "No more facts available!",
        game_over_msg: "Game Over!",

        // Difficulty levels
        easy: "Easy",
        normal: "Normal",
        hard: "Hard",
        expert: "Expert",

        // Common words
        close: "Close",
        cancel: "Cancel",
        confirm: "Confirm",
        yes: "Yes",
        no: "No",
        loading: "Loading...",
        error: "Error",
        success: "Success",

        // Additional messages
        failed_load_categories: "Failed to load categories",
        failed_load_difficulties: "Failed to load difficulties",
        enter_name_select_category: "Please enter your name, select a category and difficulty level",
        enter_name_and_difficulty: "Please enter your name and select difficulty level",
        starting_game: "Starting game...",
        game_started_get_hint: "Game started! Get your first hint!",
        no_more_facts_available: "No more facts available!",
        enter_guess: "Please enter a guess",
        similar_keep_trying: "% similar - Keep trying!",
        similar: "similar",
        correct_celebration: "🎉 Correct!",
        new_round_started: "New round started!",
        round_ended_new_round: "Round ended. Starting new round...",
        enter_name_first: "Please enter your name first",
        subcategory_hint: "Subcategory hint:",
        difficulty_info: "Difficulty:",
        fact: "Fact",

        // Offline mode
        offline_mode: "Offline Mode",
        online_mode: "Online Mode",
        start_offline_game: "Start Offline Game",
        offline_status_checking: "Checking offline availability...",
        offline_available: "Offline mode available",
        offline_unavailable: "Offline mode unavailable",
        offline_questions_available: "questions available",
        no_offline_questions: "No offline questions available",
        switch_to_online: "Switch to Online Mode",
        using_database_question: "Using question from database",

        // Rounds selection
        number_of_rounds: "Number of Rounds",
        unlimited_rounds: "♾️ Unlimited Rounds",
        one_round: "1 Round",
        three_rounds: "3 Rounds",
        five_rounds: "5 Rounds",
        ten_rounds: "10 Rounds",
        round_progress: "Round Progress",
        game_session_complete: "Game Session Complete!",
        final_score: "Final Score",
        rounds_won: "Rounds Won",
        session_summary: "Session Summary",
        play_new_session: "Play New Session",
        continue_playing: "Continue Playing",

        // Additional UI elements
        or: "or",
        offline_mode_info: "Offline mode uses previously generated questions from the database"
    },
    pl: {
        // Header and navigation
        leaderboard: "Ranking",
        my_stats: "Moje Statystyki",

        // Welcome screen
        welcome_title: "Witaj w Grze Zgadywania AI!",
        welcome_description: "Przetestuj swoją wiedzę w różnych kategoriach. Otrzymuj fakty jeden po drugim i zgaduj odpowiedź. Im mniej faktów potrzebujesz, tym wyższy twój wynik!",
        your_name: "Twoje Imię",
        enter_your_name: "Wprowadź swoje imię",
        choose_category: "Wybierz Kategorię",
        choose_category_optional: "Wybierz Kategorię (Opcjonalnie)",
        random_category: "🎲 Losowa Kategoria",
        loading_categories: "Ładowanie kategorii...",
        difficulty_level: "Poziom Trudności",
        loading_difficulties: "Ładowanie poziomów trudności...",
        language: "Język",
        start_game: "Rozpocznij Grę",

        // Game screen
        category: "Kategoria",
        round_score: "Wynik Rundy",
        total_score: "Wynik Całkowity",
        facts_revealed: "Odkryte Fakty",
        click_get_hint: "Kliknij \"Otrzymaj Wskazówkę\" aby odkryć pierwszy fakt!",
        get_hint: "Otrzymaj Wskazówkę",
        get_letter_hint: "Otrzymaj Podpowiedź Literową",
        whats_your_guess: "Jaka jest twoja odpowiedź?",
        type_your_answer: "Wpisz tutaj swoją odpowiedź...",
        submit: "Wyślij",
        new_round: "Nowa Runda",
        give_up: "Poddaj się",
        main_menu: "Menu Główne",
        
        // Hint system
        letter_hint: "Podpowiedź Literowa",
        hints_used: "Użyte Podpowiedzi",
        hints_remaining: "Pozostałe Podpowiedzi",
        letter_revealed: "Litera ujawniona!",
        no_hints_left: "Brak podpowiedzi na tę rundę",
        no_more_letters: "Nie ma więcej liter do ujawnienia",
        give_up: "Poddaj Się",
        main_menu: "Menu Główne",

        // Result modal
        congratulations: "Gratulacje!",
        correct_answer: "Poprawnie!",
        wrong_answer: "Błędna Odpowiedź",
        time_up: "Czas Minął!",
        you_got_it_right: "Trafiłeś!",
        better_luck_next_time: "Więcej szczęścia następnym razem!",
        answer: "Odpowiedź",
        time_taken: "Czas Wykonania",
        facts_used: "Użyte Fakty",
        play_again: "Zagraj Ponownie",
        change_player: "Zmień Gracza",

        // Modals
        global_leaderboard: "Globalny Ranking",
        player_statistics: "Statystyki Gracza",
        loading_leaderboard: "Ładowanie rankingu...",
        loading_statistics: "Ładowanie statystyk...",

        // Messages and notifications
        welcome_message: "Witaj w Grze Zgadywania AI!",
        connection_lost: "Utracono połączenie. Odśwież stronę.",
        fact_revealed_msg: "Nowy fakt odkryty!",
        correct_guess_msg: "Poprawnie! Dobra robota!",
        incorrect_guess_msg: "Nie całkiem. Spróbuj ponownie!",
        no_more_facts_msg: "Brak więcej dostępnych faktów!",
        game_over_msg: "Koniec Gry!",

        // Difficulty levels
        easy: "Łatwy",
        normal: "Normalny",
        hard: "Trudny",
        expert: "Ekspert",

        // Common words
        close: "Zamknij",
        cancel: "Anuluj",
        confirm: "Potwierdź",
        yes: "Tak",
        no: "Nie",
        loading: "Ładowanie...",
        error: "Błąd",
        success: "Sukces",

        // Additional messages
        failed_load_categories: "Nie udało się załadować kategorii",
        failed_load_difficulties: "Nie udało się załadować poziomów trudności",
        enter_name_select_category: "Proszę wprowadź swoje imię, wybierz kategorię i poziom trudności",
        enter_name_and_difficulty: "Proszę wprowadź swoje imię i wybierz poziom trudności",
        starting_game: "Rozpoczynanie gry...",
        game_started_get_hint: "Gra rozpoczęta! Otrzymaj swoją pierwszą wskazówkę!",
        no_more_facts_available: "Brak więcej dostępnych faktów!",
        enter_guess: "Proszę wprowadź odpowiedź",
        similar_keep_trying: "% podobne - Próbuj dalej!",
        similar: "podobne",
        correct_celebration: "🎉 Poprawnie!",
        new_round_started: "Nowa runda rozpoczęta!",
        round_ended_new_round: "Runda zakończona. Rozpoczynanie nowej rundy...",
        enter_name_first: "Proszę najpierw wprowadź swoje imię",
        subcategory_hint: "Wskazówka podkategorii:",
        difficulty_info: "Trudność:",
        fact: "Fakt",

        // Rounds selection
        number_of_rounds: "Liczba Rund",
        unlimited_rounds: "♾️ Nieograniczone Rundy",
        one_round: "1 Runda",
        three_rounds: "3 Rundy",
        five_rounds: "5 Rund",
        ten_rounds: "10 Rund",
        round_progress: "Postęp Rund",
        game_session_complete: "Sesja Gry Zakończona!",
        final_score: "Końcowy Wynik",
        rounds_won: "Wygrane Rundy",
        session_summary: "Podsumowanie Sesji",
        play_new_session: "Zagraj Nową Sesję",
        continue_playing: "Kontynuuj Grę",

        // Offline mode
        offline_mode: "Tryb Offline",
        online_mode: "Tryb Online",
        start_offline_game: "Rozpocznij Grę Offline",
        offline_status_checking: "Sprawdzanie dostępności offline...",
        offline_available: "Tryb offline dostępny",
        offline_unavailable: "Tryb offline niedostępny",
        offline_questions_available: "pytań dostępnych",
        no_offline_questions: "Brak pytań offline",
        switch_to_online: "Przełącz na Tryb Online",
        using_database_question: "Używanie pytania z bazy danych",

        // Additional UI elements 
        or: "lub",
        offline_mode_info: "Tryb offline używa wcześniej wygenerowanych pytań z bazy danych"
    }
};

class GameApp {
    constructor() {
        this.currentPlayer = '';
        this.currentCategory = '';
        this.currentDifficulty = 'normal';
        this.currentLanguage = 'en';
        this.gameActive = false;
        this.gameStarting = false; // Prevent multiple simultaneous game starts
        this.categories = [];
        this.difficulties = [];
        this.initialized = false;
        this.gameSession = null;
        this.currentFacts = [];
        this.factsRevealed = 0;

        // Round tracking for multi-round games
        this.maxRounds = null;
        this.roundsCompleted = 0;
        this.gameComplete = false;

        // Offline mode support
        this.offlineMode = false;
        this.offlineAvailable = false;
        this.offlineStats = null;
        this.offlineStatusCache = null; // Cache for offline status to avoid repeated requests

        // Initialize synchronously, then call async init
        this.initSync();
        // Note: initAsync() is called explicitly after DOM is ready
    }

    initSync() {
        this.setupEventListeners();
        this.setupLanguageSelector();
        this.updateTranslations();
    }

    async initAsync() {
        // Load essential data first (categories and difficulties)
        await Promise.all([
            this.loadCategories(),
            this.loadDifficulties()
        ]);

        // Mark as initialized and validate the start button
        this.initialized = true;
        this.validateStartButton();

        // Check offline status in background (don't wait for it)
        this.checkOfflineStatus().catch(error => {
            console.warn('Background offline status check failed:', error);
        });

        console.log('✅ GameApp initialized quickly');
    }

    // Translation methods
    t(key) {
        return translations[this.currentLanguage]?.[key] || translations.en[key] || key;
    }

    setLanguage(lang) {
        this.currentLanguage = lang;
        this.updateTranslations();

        // Update both language selectors
        const headerLanguageSelect = document.getElementById('headerLanguageSelect');
        const gameLanguageSelect = document.getElementById('languageSelect');

        if (headerLanguageSelect) headerLanguageSelect.value = lang;
        if (gameLanguageSelect) gameLanguageSelect.value = lang;

        // Save language preference
        localStorage.setItem('gameLanguage', lang);

        // Only reload categories and difficulties if we're already initialized
        // This prevents interference during initial setup
        if (this.initialized) {
            this.loadCategories();
            this.loadDifficulties();

            // Clear cache and update offline status for the new language
            this.clearOfflineStatusCache();
            this.checkOfflineStatus().catch(error => {
                console.warn('Failed to update offline status after language change:', error);
            });
        }
    }

    // Helper method to get translated category display name
    getCategoryDisplayName(categoryName) {
        if (!categoryName) {
            return this.t('random_category');
        }

        // Check if categories are loaded
        if (!this.categories || this.categories.length === 0) {
            return categoryName; // Return raw name if categories not loaded yet
        }

        const category = this.categories.find(cat => cat.name === categoryName);
        if (category) {
            return category.display_name;
        }

        // Fallback to category name if not found
        return categoryName;
    }

    updateTranslations() {
        // Update all elements with data-translate attribute
        document.querySelectorAll('[data-translate]').forEach(element => {
            const key = element.getAttribute('data-translate');
            const translation = this.t(key);

            if (element.tagName === 'INPUT' && element.type === 'text') {
                // Don't change the value, just update placeholder if it has data-translate-placeholder
                if (element.hasAttribute('data-translate-placeholder')) {
                    const placeholderKey = element.getAttribute('data-translate-placeholder');
                    element.placeholder = this.t(placeholderKey);
                }
            } else if (element.tagName === 'OPTION') {
                element.textContent = translation;
            } else {
                // For other elements, update text content while preserving HTML structure
                const icon = element.querySelector('i');
                if (icon) {
                    // Preserve icon
                    element.innerHTML = icon.outerHTML + ' ' + translation;
                } else {
                    element.textContent = translation;
                }
            }
        });

        // Update placeholder attributes
        document.querySelectorAll('[data-translate-placeholder]').forEach(element => {
            const key = element.getAttribute('data-translate-placeholder');
            element.placeholder = this.t(key);
        });

        // Update dynamic content that might not have data-translate attributes
        this.updateDynamicTranslations();
    }

    updateDynamicTranslations() {
        // Update other dynamic content based on current state
        if (this.gameActive) {
            // Update any game-specific dynamic content
        }
    }

    setupLanguageSelector() {
        // Setup header language selector
        const headerLanguageSelect = document.getElementById('headerLanguageSelect');
        if (headerLanguageSelect) {
            headerLanguageSelect.addEventListener('change', (e) => {
                this.setLanguage(e.target.value);
            });
        }

        // Load saved language preference
        const savedLanguage = localStorage.getItem('gameLanguage') || 'en';
        this.setLanguage(savedLanguage);
    }

    // HTTP-based game methods
    async httpRequest(url, method = 'GET', data = null, params = null, timeout = 10000) {
        try {
            // Add query parameters if provided
            if (params) {
                const urlObj = new URL(url, window.location.origin);
                Object.keys(params).forEach(key => urlObj.searchParams.append(key, params[key]));
                url = urlObj.toString();
            }

            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                }
            };

            if (data) {
                options.body = JSON.stringify(data);
            }

            // Create a timeout promise that rejects after the specified time
            const timeoutPromise = new Promise((_, reject) => {
                setTimeout(() => reject(new Error('Request timed out')), timeout);
            });

            // Race between the fetch request and the timeout
            const response = await Promise.race([
                fetch(url, options),
                timeoutPromise
            ]);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            if (error.message === 'Request timed out') {
                console.error('HTTP request timed out:', url);
                throw new Error('Request timed out');
            }
            console.error('HTTP request failed:', error);
            throw error;
        }
    }

    setupEventListeners() {
        console.log('🔧 Setting up event listeners...');

        // Welcome screen
        const playerNameInput = document.getElementById('playerName');
        const categorySelect = document.getElementById('categorySelect');
        const difficultySelect = document.getElementById('difficultySelect');
        const roundsSelect = document.getElementById('roundsSelect');
        const languageSelect = document.getElementById('languageSelect');
        const startGameBtn = document.getElementById('startGameBtn');

        console.log('Elements found:', {
            playerNameInput: !!playerNameInput,
            categorySelect: !!categorySelect,
            difficultySelect: !!difficultySelect,
            roundsSelect: !!roundsSelect,
            languageSelect: !!languageSelect,
            startGameBtn: !!startGameBtn
        });

        playerNameInput.addEventListener('input', () => {
            this.validateStartButton();
        });

        categorySelect.addEventListener('change', () => {
            this.validateStartButton();
            // Check offline status when category changes
            if (this.initialized) {
                this.clearOfflineStatusCache();
                this.checkOfflineStatus().catch(error => {
                    console.warn('Failed to check offline status after category change:', error);
                });
            }
        });

        difficultySelect.addEventListener('change', () => {
            this.currentDifficulty = difficultySelect.value;
            this.validateStartButton();
            // Check offline status when difficulty changes
            if (this.initialized) {
                this.clearOfflineStatusCache();
                this.checkOfflineStatus().catch(error => {
                    console.warn('Failed to check offline status after difficulty change:', error);
                });
            }
        });

        roundsSelect.addEventListener('change', () => {
            this.validateStartButton();
        });

        languageSelect.addEventListener('change', () => {
            this.currentLanguage = languageSelect.value;
            this.setLanguage(languageSelect.value);
        });

        startGameBtn.addEventListener('click', (e) => {
            console.log('🎯 START GAME BUTTON CLICKED via addEventListener!');
            console.log('Event target:', e.target);
            console.log('Button element:', startGameBtn);
            console.log('Button disabled:', startGameBtn.disabled);
            e.preventDefault();
            e.stopPropagation();

            // Only start game if not already starting or disabled
            if (!this.gameStarting && !startGameBtn.disabled) {
                this.startGame();
            } else {
                console.log('🚫 Ignoring click - game already starting or button disabled');
            }
        });

        // Add offline game button event handler
        const startOfflineGameBtn = document.getElementById('startOfflineGameBtn');
        if (startOfflineGameBtn) {
            startOfflineGameBtn.addEventListener('click', (e) => {
                console.log('🎯 START OFFLINE GAME BUTTON CLICKED!');
                e.preventDefault();
                e.stopPropagation();

                // Only start offline game if not already starting or disabled
                if (!this.gameStarting && !startOfflineGameBtn.disabled) {
                    this.startOfflineGame();
                } else {
                    console.log('🚫 Ignoring offline click - game already starting or button disabled');
                }
            });
        }

        console.log('✅ Event listeners set up complete');

        // Game screen
        const getFactBtn = document.getElementById('getFactBtn');
        const guessInput = document.getElementById('guessInput');
        const submitGuessBtn = document.getElementById('submitGuessBtn');
        const newRoundBtn = document.getElementById('newRoundBtn');
        const giveUpBtn = document.getElementById('giveUpBtn');
        const backToMenuBtn = document.getElementById('backToMenuBtn');
        const getLetterHintBtn = document.getElementById('getLetterHintBtn');

        getFactBtn.addEventListener('click', () => {
            this.requestFact();
        });

        getLetterHintBtn.addEventListener('click', () => {
            this.getLetterHint();
        });

        guessInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.submitGuess();
            }
        });

        submitGuessBtn.addEventListener('click', () => {
            this.submitGuess();
        });

        newRoundBtn.addEventListener('click', () => {
            this.startNewRound();
        });

        giveUpBtn.addEventListener('click', () => {
            this.giveUp();
        });

        backToMenuBtn.addEventListener('click', () => {
            this.backToMenu();
        });

        // Header buttons
        const leaderboardBtn = document.getElementById('leaderboardBtn');
        const statsBtn = document.getElementById('statsBtn');

        leaderboardBtn.addEventListener('click', () => {
            this.showLeaderboard();
        });

        statsBtn.addEventListener('click', () => {
            this.showStats();
        });

        // Modal buttons
        const playAgainBtn = document.getElementById('playAgainBtn');
        const changePlayerBtn = document.getElementById('changePlayerBtn');

        playAgainBtn.addEventListener('click', () => {
            this.playAgain();
        });

        changePlayerBtn.addEventListener('click', () => {
            this.changePlayer();
        });

        // Close modal buttons
        document.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modalId = e.target.closest('.close-btn').dataset.modal;
                this.closeModal(modalId);
            });
        });

        // Click outside modal to close
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });
    }

    async loadCategories() {
        try {
            const response = await fetch(`/api/categories?lang=${this.currentLanguage}`);
            const categories = await response.json();

            if (response.ok) {
                this.categories = categories;
                this.populateCategorySelect();
            } else {
                throw new Error('Failed to load categories');
            }
        } catch (error) {
            console.error('Error loading categories:', error);
            this.showToast(this.t('failed_load_categories'), 'error');
        }
    }

    populateCategorySelect() {
        const select = document.getElementById('categorySelect');
        const currentValue = select.value; // Preserve current selection
        select.innerHTML = `<option value="">${this.t('random_category')}</option>`;

        this.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.name;
            option.textContent = `${category.display_name.charAt(0).toUpperCase() + category.display_name.slice(1)} - ${category.display_description}`;
            select.appendChild(option);
        });

        // Restore selection if it was set
        if (currentValue) {
            select.value = currentValue;
        }
    }

    async loadDifficulties() {
        try {
            const response = await fetch(`/api/difficulties?lang=${this.currentLanguage}`);
            const data = await response.json();

            if (response.ok) {
                this.difficulties = data;
                this.populateDifficultySelect();
            } else {
                throw new Error('Failed to load difficulties');
            }
        } catch (error) {
            console.error('Error loading difficulties:', error);
            this.showToast(this.t('failed_load_difficulties'), 'error');
        }
    }

    populateDifficultySelect() {
        const difficultySelect = document.getElementById('difficultySelect');
        const currentValue = difficultySelect.value; // Preserve current selection

        // Clear options but don't add loading option to avoid triggering validation
        difficultySelect.innerHTML = '';

        this.difficulties.forEach(difficulty => {
            const option = document.createElement('option');
            option.value = difficulty.name;
            option.textContent = `${difficulty.display_name} (${difficulty.score_multiplier}x points)`;
            if (difficulty.description) {
                option.title = difficulty.description;
            }
            difficultySelect.appendChild(option);
        });

        // Set default or restore selection
        if (currentValue && this.difficulties.find(d => d.name === currentValue)) {
            difficultySelect.value = currentValue;
            this.currentDifficulty = currentValue;
        } else {
            // Set default to normal
            difficultySelect.value = 'normal';
            this.currentDifficulty = 'normal';
        }

        this.validateStartButton();
    }

    validateStartButton() {
        // Don't validate before initialization is complete
        if (!this.initialized) {
            return;
        }

        const playerNameInput = document.getElementById('playerName');
        const startBtn = document.getElementById('startGameBtn');

        // Extra safety checks
        if (!playerNameInput || !startBtn) {
            return;
        }

        const playerName = playerNameInput.value.trim();
        const shouldBeEnabled = !!playerName;

        // Use removeAttribute/setAttribute for more reliable disabled handling
        if (shouldBeEnabled) {
            startBtn.disabled = false;
            startBtn.removeAttribute('disabled');
        } else {
            startBtn.disabled = true;
            startBtn.setAttribute('disabled', 'disabled');
        }
    }

    async startGame() {
        console.log('🎮 Start Game button clicked!');

        // Prevent multiple simultaneous game starts
        const startGameBtn = document.getElementById('startGameBtn');
        if (this.gameStarting || startGameBtn?.disabled) {
            console.log('🚫 Game start already in progress, ignoring duplicate request');
            return;
        }

        // Mark game as starting and disable button
        this.gameStarting = true;
        if (startGameBtn) {
            startGameBtn.disabled = true;
            startGameBtn.setAttribute('disabled', 'true');
            startGameBtn.textContent = this.t('starting_game') || 'Starting game...';
        }

        const playerName = document.getElementById('playerName').value.trim();
        const category = document.getElementById('categorySelect').value;
        const difficulty = document.getElementById('difficultySelect').value || 'normal';
        const rounds = document.getElementById('roundsSelect').value;

        console.log('Game start data:', { playerName, category, difficulty, rounds });

        if (!playerName) {
            this.showToast(this.t('enter_name_first'), 'warning');
            // Reset button state on validation failure
            this.gameStarting = false;
            if (startGameBtn) {
                startGameBtn.disabled = false;
                startGameBtn.removeAttribute('disabled');
                startGameBtn.textContent = this.t('start_game') || 'Start Game';
            }
            return;
        }

        this.currentPlayer = playerName;
        this.currentCategory = category;
        this.currentDifficulty = difficulty;
        this.maxRounds = rounds ? parseInt(rounds) : null;
        this.roundsCompleted = 0;
        this.gameComplete = false;

        try {
            // Start game via HTTP request
            const gameData = await this.httpRequest('/api/start_game', 'POST', {
                player_name: playerName,
                category: category,
                difficulty: difficulty,
                language: this.currentLanguage,
                max_rounds: this.maxRounds
            });

            console.log('✅ Game started:', gameData);
            this.handleGameStarted(gameData);

        } catch (error) {
            console.error('❌ Failed to start game:', error);
            this.showToast('Failed to start game. Please try again.', 'error');

            // Reset button state on error
            this.gameStarting = false;
            if (startGameBtn) {
                startGameBtn.disabled = false;
                startGameBtn.removeAttribute('disabled');
                startGameBtn.textContent = this.t('start_game') || 'Start Game';
            }
        }
    }

    handleGameStarted(data) {
        console.log('🎯 Game started event received:', data);

        // Reset game starting state and button
        this.gameStarting = false;
        const startGameBtn = document.getElementById('startGameBtn');
        if (startGameBtn) {
            startGameBtn.disabled = false;
            startGameBtn.removeAttribute('disabled');
            startGameBtn.textContent = this.t('start_game') || 'Start Game';
        }

        this.gameActive = true;
        this.gameSession = data.session_id;
        this.currentFacts = [];
        this.factsRevealed = 0;

        // Update round tracking
        this.maxRounds = data.max_rounds;
        this.roundsCompleted = data.rounds_completed || 0;
        this.gameComplete = false;

        // Update UI
        document.getElementById('currentPlayer').textContent = this.currentPlayer;

        // Display category with proper translation and subcategory
        let categoryDisplay = this.getCategoryDisplayName(data.category);
        if (data.subcategory) {
            categoryDisplay += ` - ${data.subcategory}`;
        }
        document.getElementById('currentCategory').textContent = categoryDisplay;

        document.getElementById('totalFacts').textContent = data.facts_available;

        // Initialize hint system
        if (data.hints_available) {
            document.getElementById('maxHints').textContent = data.hints_available;
            document.getElementById('hintsUsed').textContent = data.hints_used || '0';
        }

        // Update round progress display
        this.updateRoundProgress();

        // Display difficulty and subcategory info if available
        // Removed toast notification for difficulty info

        // Reset game state
        this.resetGameState();

        // Switch to game screen
        this.showScreen('gameScreen');

        // Removed "game started" toast
    }

    updateRoundProgress() {
        const progressDisplay = document.getElementById('roundProgressDisplay');
        const progressText = document.getElementById('roundProgress');

        if (this.maxRounds && this.maxRounds > 0) {
            progressDisplay.style.display = 'block';
            progressText.textContent = `${this.roundsCompleted + 1}/${this.maxRounds}`;
        } else {
            progressDisplay.style.display = 'none';
        }
    }

    resetGameState() {
        document.getElementById('factsList').innerHTML = `
            <div class="no-facts">
                <i class="fas fa-question-circle"></i>
                <p>Click "Get Hint" to reveal your first fact!</p>
            </div>
        `;
        document.getElementById('guessHistory').innerHTML = '';
        document.getElementById('factsShown').textContent = '0';
        document.getElementById('roundScore').textContent = '0';
        document.getElementById('guessInput').value = '';
        document.getElementById('getFactBtn').disabled = false;
        document.getElementById('submitGuessBtn').disabled = false;
        document.getElementById('newRoundBtn').style.display = 'none';
        
        // Reset hint system
        document.getElementById('letterHintDisplay').style.display = 'none';
        document.getElementById('hintLetters').textContent = '';
        document.getElementById('hintsUsed').textContent = '0';
        document.getElementById('maxHints').textContent = '3';
        const letterHintBtn = document.getElementById('getLetterHintBtn');
        letterHintBtn.disabled = false;
        letterHintBtn.innerHTML = `<i class="fas fa-font"></i> ${this.t('get_letter_hint')}`;
    }

    async requestFact() {
        try {
            document.getElementById('getFactBtn').disabled = true;

            const response = await this.httpRequest('/api/request_fact', 'POST', {
                session_id: this.gameSession,
                language: this.currentLanguage
            });

            this.handleFactRevealed(response);

        } catch (error) {
            console.error('❌ Failed to get fact:', error);
            this.showToast('Failed to get fact. Please try again.', 'error');
        } finally {
            setTimeout(() => {
                document.getElementById('getFactBtn').disabled = false;
            }, 1000);
        }
    }

    handleFactRevealed(data) {
        const factsList = document.getElementById('factsList');

        // Remove no-facts message if present
        const noFacts = factsList.querySelector('.no-facts');
        if (noFacts) {
            noFacts.remove();
        }

        // Add new fact
        const factElement = document.createElement('div');
        factElement.className = 'fact-item';
        factElement.innerHTML = `
            <div class="fact-number">${this.t('fact')} ${data.fact_number}:</div>
            <div class="fact-text">${data.fact}</div>
        `;

        factsList.appendChild(factElement);

        // Update counter
        document.getElementById('factsShown').textContent = data.fact_number;

        // Scroll to bottom
        factsList.scrollTop = factsList.scrollHeight;
    }

    handleNoMoreFacts() {
        document.getElementById('getFactBtn').disabled = true;
        document.getElementById('getFactBtn').innerHTML = '<i class="fas fa-ban"></i> No More Hints';
        this.showToast(this.t('no_more_facts_available'), 'warning');
    }

    async getLetterHint() {
        try {
            const button = document.getElementById('getLetterHintBtn');
            const originalText = button.innerHTML;
            
            // Disable button and show loading
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Getting Hint...';

            const response = await this.httpRequest('/api/get_hint', 'POST', {
                session_id: this.gameSession,
                language: this.currentLanguage
            });

            this.handleLetterHintResponse(response);

        } catch (error) {
            console.error('❌ Failed to get letter hint:', error);
            this.showToast('Failed to get hint. Please try again.', 'error');
        } finally {
            setTimeout(() => {
                const button = document.getElementById('getLetterHintBtn');
                button.disabled = false;
                button.innerHTML = `<i class="fas fa-font"></i> ${this.t('get_letter_hint')}`;
            }, 1000);
        }
    }

    handleLetterHintResponse(data) {
        if (data.success) {
            // Show hint display
            const hintDisplay = document.getElementById('letterHintDisplay');
            const hintLetters = document.getElementById('hintLetters');
            const hintsUsed = document.getElementById('hintsUsed');
            const maxHints = document.getElementById('maxHints');

            hintDisplay.style.display = 'block';
            hintLetters.textContent = data.hint_display;
            hintsUsed.textContent = data.hints_used;
            maxHints.textContent = data.max_hints;

            // Disable button if no more hints available
            if (data.hints_remaining === 0) {
                const button = document.getElementById('getLetterHintBtn');
                button.disabled = true;
                button.innerHTML = '<i class="fas fa-ban"></i> No More Hints';
            }

            this.showToast(data.message, 'success');
        } else {
            this.showToast(data.message, 'warning');
        }
    }

    async submitGuess() {
        const guessInput = document.getElementById('guessInput');
        const guess = guessInput.value.trim();

        if (!guess) {
            this.showToast(this.t('enter_guess'), 'warning');
            return;
        }

        try {
            // Add to guess history
            this.addGuessToHistory(guess, 'pending');

            // Clear input
            guessInput.value = '';

            // Submit to server
            const response = await this.httpRequest('/api/submit_guess', 'POST', {
                session_id: this.gameSession,
                guess: guess
            });

            this.handleGuessResult(response);

        } catch (error) {
            console.error('❌ Failed to submit guess:', error);
            this.showToast('Failed to submit guess. Please try again.', 'error');
        }
    }

    addGuessToHistory(guess, status, similarity = null) {
        const guessHistory = document.getElementById('guessHistory');
        const guessElement = document.createElement('div');
        guessElement.className = `guess-item ${status}`;

        let similarityDisplay = '';
        if (status === 'incorrect' || status === 'pending') {
            // Always show similarity for incorrect and pending guesses, even if 0%
            const similarityPercent = similarity ? Math.round(similarity * 100) : 0;
            similarityDisplay = `<span class="similarity-info">${similarityPercent}% ${this.t('similar')}</span>`;
        }

        let statusIcon;
        if (status === 'pending') {
            statusIcon = '<i class="fas fa-spinner fa-spin"></i>';
        } else if (status === 'correct') {
            statusIcon = '<i class="fas fa-check text-success"></i>';
        } else {
            statusIcon = '<i class="fas fa-times text-danger"></i>';
        }

        guessElement.innerHTML = `
            <span class="guess-text">${guess}</span>
            <div class="guess-info">
                ${similarityDisplay}
                <span class="guess-status">
                    ${statusIcon}
                </span>
            </div>
        `;

        guessHistory.appendChild(guessElement);
        guessHistory.scrollTop = guessHistory.scrollHeight;

        return guessElement;
    }

    handleGuessResult(data) {
        console.log('🔍 Guess result received:', data); // Debug log

        this.updateLastGuessStatus(data);
        this.processGuessOutcome(data);
    }

    updateLastGuessStatus(data) {
        const lastGuess = document.querySelector('.guess-item:last-child');
        if (!lastGuess) return;

        lastGuess.className = `guess-item ${data.correct ? 'correct' : 'incorrect'}`;
        this.updateGuessInfo(lastGuess, data);
    }

    updateGuessInfo(guessElement, data) {
        const guessInfo = guessElement.querySelector('.guess-info');
        if (!guessInfo) return;

        let similarityDisplay = '';
        if (!data.correct) {
            const similarityPercent = data.similarity ? Math.round(data.similarity * 100) : 0;
            similarityDisplay = `<span class="similarity-info">${similarityPercent}% ${this.t('similar')}</span>`;
            console.log('📊 Similarity display:', similarityDisplay); // Debug log
        }

        guessInfo.innerHTML = `
            ${similarityDisplay}
            <span class="guess-status">
                ${data.correct ? '<i class="fas fa-check"></i>' : '<i class="fas fa-times"></i>'}
            </span>
        `;
    }

    processGuessOutcome(data) {
        if (data.correct) {
            this.handleCorrectGuess(data);
        } else if (data.auto_revealed) {
            this.handleAutoRevealedAnswer(data);
        }
        // No action needed for regular incorrect guesses - similarity is shown inline
    }

    handleCorrectGuess(data) {
        this.gameActive = false;

        // Update scores
        document.getElementById('roundScore').textContent = data.score || 0;
        document.getElementById('totalScore').textContent = data.total_score || 0;

        // Update round tracking
        this.roundsCompleted = data.rounds_completed || this.roundsCompleted + 1;
        this.gameComplete = data.game_complete || false;
        this.updateRoundProgress();

        // Disable game controls
        document.getElementById('getFactBtn').disabled = true;
        document.getElementById('submitGuessBtn').disabled = true;

        // Check if game is complete
        if (this.gameComplete) {
            // Hide new round button and show session complete options
            document.getElementById('newRoundBtn').style.display = 'none';
            this.showGameCompleteModal(data);
        } else {
            // Show new round button for continuing the session
            document.getElementById('newRoundBtn').style.display = 'inline-flex';
            this.showResultModal(data, true);
        }

        // Enhanced success message
        const timeTaken = Math.round(data.time_taken || 0);
        const factsUsed = data.facts_used || 0;
        const scoreMsg = `+${data.score} points! (${factsUsed} facts, ${timeTaken}s)`;

        this.showToast(this.t('correct_celebration') + ' ' + scoreMsg, 'success');
    }

    handleAutoRevealedAnswer(data) {
        this.gameActive = false;

        // Update scores (no score for auto-revealed)
        document.getElementById('roundScore').textContent = '0';
        document.getElementById('totalScore').textContent = data.total_score || 0;

        // Update round tracking
        this.roundsCompleted = data.rounds_completed || this.roundsCompleted + 1;
        this.gameComplete = data.game_complete || false;
        this.updateRoundProgress();

        // Disable game controls
        document.getElementById('getFactBtn').disabled = true;
        document.getElementById('submitGuessBtn').disabled = true;

        // Check if game is complete
        if (this.gameComplete) {
            // Hide new round button and show session complete options
            document.getElementById('newRoundBtn').style.display = 'none';
            this.showGameCompleteModal(data);
        } else {
            // Show new round button for continuing the session
            document.getElementById('newRoundBtn').style.display = 'inline-flex';
            this.showResultModal(data, false); // false = not a success
        }

        // Show auto-reveal message
        const feedbackMessage = data.feedback || this.t('answer_revealed_attempts');
        this.showToast(feedbackMessage);
        document.getElementById('timeTaken').textContent = `${(data.time_taken || 0).toFixed(1)}s`;
        document.getElementById('factsUsed').textContent = data.facts_used || 0;

        // Change "Play Again" button text to "Play New Session"
        const playAgainBtn = document.querySelector('#resultModal .btn-primary');
        if (playAgainBtn) {
            playAgainBtn.textContent = this.t('play_new_session');
        }

        // Show modal
        modal.classList.add('active');

        // Show final score toast
        this.showToast(`${this.t('final_score')}: ${data.total_score} points!`, 'success');
    }

    showResultModal(data, success) {
        const modal = document.getElementById('resultModal');
        const icon = document.getElementById('resultIcon');
        const title = document.getElementById('resultTitle');
        const message = document.getElementById('resultMessage');

        // Update content
        if (success) {
            icon.className = 'result-icon success';
            icon.innerHTML = '<i class="fas fa-check-circle"></i>';
            title.textContent = this.t('congratulations');
            message.textContent = this.t('you_got_it_right');
        } else {
            icon.className = 'result-icon failure';
            icon.innerHTML = '<i class="fas fa-times-circle"></i>';
            title.textContent = this.t('game_over_msg');
            message.textContent = this.t('better_luck_next_time');
        }

        // Update stats
        document.getElementById('correctAnswer').textContent = data.answer || '-';
        document.getElementById('finalRoundScore').textContent = data.score || 0;
        document.getElementById('timeTaken').textContent = `${(data.time_taken || 0).toFixed(1)}s`;
        document.getElementById('factsUsed').textContent = data.facts_used || 0;

        // Show modal
        modal.classList.add('active');
    }

    async startNewRound() {
        try {
            // Check if we're in offline mode and use appropriate route
            if (this.offlineMode) {
                await this.startOfflineNewRound();
                return;
            }

            const response = await this.httpRequest('/api/new_round', 'POST', {
                session_id: this.gameSession,
                category: this.currentCategory,
                difficulty: this.currentDifficulty,
                language: this.currentLanguage
            });

            this.handleNewRoundStarted(response);

        } catch (error) {
            console.error('❌ Failed to start new round:', error);
            this.showToast('Failed to start new round. Please try again.', 'error');
        }
    }

    handleNewRoundStarted(data) {
        this.gameActive = true;
        this.gameComplete = data.game_complete || false;
        this.roundsCompleted = data.rounds_completed || this.roundsCompleted;

        this.resetGameState();
        this.updateRoundProgress();

        // Display category with proper translation and subcategory
        let categoryDisplay = this.getCategoryDisplayName(data.category);
        if (data.subcategory) {
            categoryDisplay += ` - ${data.subcategory}`;
        }
        document.getElementById('currentCategory').textContent = categoryDisplay;

        document.getElementById('totalFacts').textContent = data.facts_available;

        // Display subcategory hint if available
        // Removed subcategory hint toast for new round

        // Removed "new round started" toast
    }

    giveUp() {
        if (confirm('Are you sure you want to give up this round?')) {
            // You could implement a give up feature here
            this.showToast(this.t('round_ended_new_round'), 'warning');
            this.startNewRound();
        }
    }

    backToMenu() {
        if (this.gameActive && !confirm('Are you sure you want to exit the current game?')) {
            return;
        }

        this.showScreen('welcomeScreen');
        this.gameActive = false;

        // Refresh offline status when returning to main menu
        this.checkOfflineStatus().catch(error => {
            console.warn('Failed to refresh offline status on menu return:', error);
        });
    }

    playAgain() {
        console.log('🔄 Play Again clicked! Game complete:', this.gameComplete);
        this.closeModal('resultModal');

        // If the game session is complete, start a completely new game
        if (this.gameComplete) {
            console.log('🆕 Starting completely new game...');
            this.startNewGame();
        } else {
            // Otherwise, start a new round in the current session
            console.log('🔄 Starting new round in current session...');
            this.startNewRound();
        }
    }

    async startNewGame() {
        try {
            console.log('🎮 Starting completely new game session...');
            console.log('Previous session ID:', this.gameSession);

            // Reset game state variables
            this.gameSession = null;
            this.gameComplete = false;
            this.roundsCompleted = 0;
            this.gameActive = false;
            this.currentFacts = [];
            this.factsRevealed = 0;

            console.log('Game settings:', {
                player: this.currentPlayer,
                category: this.currentCategory,
                difficulty: this.currentDifficulty,
                maxRounds: this.maxRounds,
                language: this.currentLanguage
            });

            // Start a completely new game with the same settings
            const response = await this.httpRequest('/api/start_game', 'POST', {
                player_name: this.currentPlayer,
                category: this.currentCategory,
                difficulty: this.currentDifficulty,
                max_rounds: this.maxRounds,
                language: this.currentLanguage
            });

            console.log('✅ New game started successfully:', response);
            this.handleGameStarted(response);

        } catch (error) {
            console.error('❌ Failed to start new game:', error);
            this.showToast('Failed to start new game. Please try again.', 'error');
        }
    }

    changePlayer() {
        this.closeModal('resultModal');

        // Reset all game state
        this.gameSession = null;
        this.gameComplete = false;
        this.roundsCompleted = 0;
        this.gameActive = false;
        this.currentFacts = [];
        this.factsRevealed = 0;

        // Go back to welcome screen and clear player name
        this.backToMenu();
        document.getElementById('playerName').value = '';
        document.getElementById('categorySelect').value = '';
        this.validateStartButton();
    }

    async showLeaderboard() {
        const modal = document.getElementById('leaderboardModal');
        const content = document.getElementById('leaderboardContent');

        content.innerHTML = `
            <div class="loading">
                <i class="fas fa-spinner fa-spin"></i>
                ${this.t('loading_leaderboard')}
            </div>
        `;

        modal.classList.add('active');

        try {
            const response = await fetch('/api/leaderboard');
            const data = await response.json();

            if (response.ok) {
                this.renderTextBasedLeaderboard(content, data.leaderboard);
            } else {
                throw new Error(data.error || 'Failed to load leaderboard');
            }
        } catch (error) {
            console.error('Error loading leaderboard:', error);
            content.innerHTML = `
                <div class="error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Failed to load leaderboard</p>
                </div>
            `;
        }
    }

    addMonospaceStyles() {
        if (!document.getElementById('monospaceStyles')) {
            const styles = document.createElement('style');
            styles.id = 'monospaceStyles';
            styles.textContent = `
                .monospace-content {
                    font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
                    padding: 20px;
                    background: #fff;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    max-height: calc(80vh - 120px);
                    overflow-y: auto;
                }

                .monospace-content pre {
                    margin: 0;
                    padding: 0;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    font-size: 14px;
                    line-height: 1.6;
                    color: #333;
                }

                /* Custom scrollbar */
                .monospace-content::-webkit-scrollbar {
                    width: 8px;
                }
                
                .monospace-content::-webkit-scrollbar-track {
                    background: #f1f1f1;
                    border-radius: 4px;
                }
                
                .monospace-content::-webkit-scrollbar-thumb {
                    background: #c1c1c1;
                    border-radius: 4px;
                }

                @media (max-width: 768px) {
                    .monospace-content {
                        padding: 15px;
                        max-height: calc(80vh - 100px);
                    }
                    .monospace-content pre {
                        font-size: 12px;
                        line-height: 1.5;
                    }
                }

                @media (max-width: 480px) {
                    .monospace-content {
                        padding: 12px;
                        max-height: calc(85vh - 80px);
                    }
                    .monospace-content pre {
                        font-size: 11px;
                        line-height: 1.4;
                    }
                }
            `;
            document.head.appendChild(styles);
        }
    }

    renderTextBasedLeaderboard(container, leaderboardText) {
        console.log('📊 Rendering text-based leaderboard');
        container.innerHTML = `
            <div class="modal-body monospace-content">
                <pre>${leaderboardText}</pre>
            </div>
        `;
        this.addMonospaceStyles();
    }

    async showStats() {
        if (!this.currentPlayer) {
            this.showToast(this.t('enter_name_first'), 'warning');
            return;
        }

        const modal = document.getElementById('statsModal');
        const content = document.getElementById('statsContent');

        content.innerHTML = `
            <div class="loading">
                <i class="fas fa-spinner fa-spin"></i>
                Loading statistics...
            </div>
        `;

        modal.classList.add('active');

        try {
            const response = await fetch(`/api/player/${encodeURIComponent(this.currentPlayer)}/stats`);
            const data = await response.json();

            if (response.ok) {
                this.renderTextBasedStats(content, data.stats);
            } else {
                throw new Error(data.error || 'Failed to load statistics');
            }
        } catch (error) {
            console.error('Error loading stats:', error);
            content.innerHTML = `
                <div class="error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Failed to load statistics</p>
                </div>
            `;
        }
    }

    renderTextBasedStats(container, statsText) {
        console.log('📈 Rendering text-based stats');
        container.innerHTML = `
            <div class="modal-body monospace-content">
                <pre>${statsText}</pre>
            </div>
        `;
        this.addMonospaceStyles();
    }

    showScreen(screenId) {
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        document.getElementById(screenId).classList.add('active');
    }

    closeModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
    }

    showToast(message, type = 'info') {
        // Toast messages disabled - no visual notifications will be shown
        return;
    }

    async checkOfflineStatus() {
        /**Check if offline mode is available and get statistics**/

        // Check if we have recent cached data (less than 30 seconds old) for the current language, category, and difficulty
        const currentCategory = document.getElementById('categorySelect')?.value || '';
        const currentDifficulty = document.getElementById('difficultySelect')?.value || 'normal';
        const cacheKey = `${this.currentLanguage}_${currentCategory}_${currentDifficulty}`;

        if (this.offlineStatusCache &&
            (Date.now() - this.offlineStatusCache.timestamp < 30000) &&
            this.offlineStatusCache.cacheKey === cacheKey) {
            console.log('📦 Using cached offline status for', cacheKey);
            const cachedResponse = this.offlineStatusCache.data;

            this.offlineAvailable = cachedResponse.offline_available;
            this.offlineStats = {
                available_questions: cachedResponse.unused_questions,
                total_questions: cachedResponse.total_questions,
                used_questions: cachedResponse.used_questions,
                categories: cachedResponse.categories
            };

            this.updateOfflineUI();
            return cachedResponse;
        }

        // Show checking status immediately
        this.updateOfflineUI(true); // true = checking state

        try {
            // Get current category and difficulty for the check
            const currentCategory = document.getElementById('categorySelect')?.value || '';
            const currentDifficulty = document.getElementById('difficultySelect')?.value || 'normal';

            // Use very short timeout for offline status check (2 seconds)
            const response = await this.httpRequest('/api/offline_status', 'GET', null, {
                lang: this.currentLanguage,
                category: currentCategory,
                difficulty: currentDifficulty
            }, 3000);

            this.offlineAvailable = response.offline_available;
            this.offlineStats = {
                available_questions: response.unused_questions,
                total_questions: response.total_questions,
                used_questions: response.used_questions,
                categories: response.categories
            };

            // Cache the result for 30 seconds to avoid repeated requests
            this.offlineStatusCache = {
                timestamp: Date.now(),
                cacheKey: cacheKey,
                data: response
            };

            // Update UI elements
            this.updateOfflineUI();

            console.log('✅ Offline status checked:', this.offlineAvailable ? 'Available' : 'Unavailable');
            return response;

        } catch (error) {
            console.warn('⚠️ Offline status check failed (quick timeout):', error.message);

            // Set unavailable state
            this.offlineAvailable = false;
            this.offlineStats = null;
            this.updateOfflineUI();

            return { offline_available: false, reason: error.message || 'Connection error' };
        }
    }

    updateOfflineUI(isChecking = false) {
        /**Update UI elements related to offline mode**/
        this.updateOfflineButton(isChecking);
        this.updateOfflineStatus(isChecking);
    }

    updateOfflineButton(isChecking) {
        /**Update the offline game button state**/
        const offlineButton = document.getElementById('startOfflineGameBtn');
        if (!offlineButton) return;

        if (isChecking) {
            // Show checking state
            offlineButton.disabled = true;
            offlineButton.textContent = this.t('offline_status_checking');
            offlineButton.classList.add('disabled');
        } else {
            // Enable button if there are any questions available
            const totalCount = this.offlineStats?.total_questions || 0;
            const hasQuestions = totalCount > 0;

            offlineButton.disabled = !hasQuestions;
            if (hasQuestions) {
                offlineButton.textContent = this.t('start_offline_game');
                offlineButton.classList.remove('disabled');
            } else {
                offlineButton.textContent = this.t('no_offline_questions');
                offlineButton.classList.add('disabled');
            }
        }
    }

    updateOfflineStatus(isChecking) {
        /**Update the offline status display**/
        const offlineStatus = document.getElementById('offlineStatus');
        if (!offlineStatus) return;

        if (isChecking) {
            // Show checking state
            offlineStatus.textContent = this.t('offline_status_checking');
            offlineStatus.className = 'offline-status checking';
        } else if (this.offlineStats) {
            this.showOfflineStatsStatus(offlineStatus);
        } else {
            // Show unavailable state
            offlineStatus.textContent = this.t('offline_unavailable');
            offlineStatus.className = 'offline-status unavailable';
        }
    }

    showOfflineStatsStatus(offlineStatus) {
        /**Show status based on available questions data**/
        const totalCount = this.offlineStats.total_questions || 0;

        if (totalCount > 0) {
            // Has questions available
            offlineStatus.textContent = `${this.t('offline_available')}: ${totalCount} ${this.t('offline_questions_available')}`;
            offlineStatus.className = 'offline-status available';
        } else {
            // No questions at all
            offlineStatus.textContent = 'No offline questions in database';
            offlineStatus.className = 'offline-status unavailable';
        }
    }

    async startOfflineGame() {
        /**Start a game in offline mode using database questions**/
        console.log('🎮 Start Offline Game button clicked!');

        if (!this.validateOfflineGameStart()) {
            return;
        }

        const gameParams = this.prepareOfflineGameParams();
        if (!gameParams) {
            return;
        }

        try {
            const gameData = await this.httpRequest('/api/start_offline_game', 'POST', gameParams);
            console.log('✅ Offline game started:', gameData);
            this.handleGameStarted(gameData);
        } catch (error) {
            this.handleOfflineGameStartError(error);
        }
    }

    validateOfflineGameStart() {
        /**Validate if offline game can be started**/
        const startOfflineBtn = document.getElementById('startOfflineGameBtn');

        // Prevent multiple simultaneous game starts
        if (this.gameStarting || startOfflineBtn?.disabled) {
            console.log('🚫 Offline game start already in progress, ignoring duplicate request');
            return false;
        }

        // Mark game as starting and disable button
        this.gameStarting = true;
        if (startOfflineBtn) {
            startOfflineBtn.disabled = true;
            startOfflineBtn.setAttribute('disabled', 'true');
            startOfflineBtn.textContent = this.t('starting_game') || 'Starting game...';
        }

        return true;
    }

    prepareOfflineGameParams() {
        /**Prepare game parameters for offline game**/
        const playerName = document.getElementById('playerName').value.trim();
        const category = document.getElementById('categorySelect').value;
        const difficulty = document.getElementById('difficultySelect').value || 'normal';
        const rounds = document.getElementById('roundsSelect').value;

        console.log('Offline game start data:', { playerName, category, difficulty, rounds });

        if (!playerName) {
            this.showToast(this.t('enter_name_first'), 'warning');
            this.resetOfflineGameButton();
            return null;
        }

        // Set game state
        this.currentPlayer = playerName;
        this.currentCategory = category;
        this.currentDifficulty = difficulty;
        this.maxRounds = rounds ? parseInt(rounds) : null;
        this.roundsCompleted = 0;
        this.gameComplete = false;
        this.offlineMode = true;

        return {
            player_name: playerName,
            category: category,
            difficulty: difficulty,
            language: this.currentLanguage,
            max_rounds: this.maxRounds
        };
    }

    handleOfflineGameStartError(error) {
        /**Handle errors when starting offline game**/
        console.error('❌ Failed to start offline game:', error);

        const errorInfo = this.parseOfflineGameError(error);
        this.showToast(errorInfo.message, 'warning');

        if (errorInfo.shouldSuggestAlternatives) {
            this.showOfflineGameSuggestions();
        }

        this.resetOfflineGameButton();
    }

    parseOfflineGameError(error) {
        /**Parse error response for offline game start**/
        let errorMessage = 'Failed to start offline game. Please try again or use online mode.';
        let shouldSuggestAlternatives = false;

        try {
            // Check if error has a response property (fetch error)
            if (error.response) {
                const errorData = error.response.json();
                if (errorData.error === 'No offline questions available') {
                    errorMessage = errorData.message || 'No offline questions available for this combination of category, difficulty, and language.';
                    shouldSuggestAlternatives = true;
                } else {
                    errorMessage = errorData.error || errorData.message || errorMessage;
                }
            } else if (error.message) {
                // Handle string error messages
                if (error.message.includes('No offline questions') || error.message.includes('available_questions": 0')) {
                    errorMessage = 'No offline questions available for the selected category, difficulty, and language combination.';
                    shouldSuggestAlternatives = true;
                } else {
                    errorMessage = error.message;
                }
            }
        } catch (parseError) {
            console.warn('Could not parse error response:', parseError);
            // Use default message if parsing fails
        }

        return { message: errorMessage, shouldSuggestAlternatives };
    }

    showOfflineGameSuggestions() {
        /**Show helpful suggestions when offline game fails**/
        // Refresh offline status to get updated information
        this.clearOfflineStatusCache();
        this.checkOfflineStatus().catch(statusError => {
            console.warn('Failed to refresh offline status after error:', statusError);
        });

        // Show suggestions after a brief delay
        setTimeout(() => {
            this.showToast('💡 Try: Change category to "Random", switch difficulty, or use online mode for unlimited questions.', 'info');
        }, 2000);

        // Auto-suggest switching to random category if a specific one was selected
        const categorySelect = document.getElementById('categorySelect');
        if (categorySelect?.value) {
            setTimeout(() => {
                this.showToast('💭 Suggestion: Try selecting "Random Category" for more offline questions.', 'info');
            }, 4000);
        }
    }

    resetOfflineGameButton() {
        /**Reset the offline game button state**/
        this.gameStarting = false;
        this.offlineMode = false;
        const startOfflineBtn = document.getElementById('startOfflineGameBtn');
        if (startOfflineBtn) {
            startOfflineBtn.disabled = false;
            startOfflineBtn.removeAttribute('disabled');
            startOfflineBtn.textContent = this.t('start_offline_game');
        }
    }

    async startOfflineNewRound() {
        /**Start a new round in offline mode**/
        try {
            const gameData = await this.httpRequest('/api/offline-new-round', 'POST', {
                session_id: this.gameSession,
                category: this.currentCategory,
                difficulty: this.currentDifficulty,
                language: this.currentLanguage
            });

            console.log('✅ Offline new round started:', gameData);
            this.handleNewRoundStarted(gameData);

        } catch (error) {
            console.error('❌ Failed to start offline new round:', error);
            this.showToast('Failed to start new round. Switching to online mode.', 'error');
            // Fall back to online mode
            this.offlineMode = false;
            this.startNewRound();
        }
    }

    clearOfflineStatusCache() {
        /**Clear the offline status cache to force a fresh check**/
        this.offlineStatusCache = null;
        console.log('🗑️ Offline status cache cleared');
    }
}

// Initialize the game when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 DOM loaded, initializing game...');
    window.gameApp = new GameApp();
    // Initialize async functionality after DOM is ready
    window.gameApp.initAsync();
});
