document.addEventListener('DOMContentLoaded', function() {
    // Search functionality with suggestions
    const searchBar = document.getElementById('search-bar');
    const searchSuggestions = document.getElementById('search-suggestions');
    
    if (searchBar && searchSuggestions) {
        searchBar.addEventListener('input', function() {
            const query = this.value.trim();
            
            if (query.length > 2) {
                // In a real app, this would be an AJAX call to the server
                const suggestions = getSearchSuggestions(query);
                displaySuggestions(suggestions);
            } else {
                searchSuggestions.style.display = 'none';
            }
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (e.target !== searchBar) {
                searchSuggestions.style.display = 'none';
            }
        });
    }
    
    // Anime card hover effects
    const animeCards = document.querySelectorAll('.anime-card');
    animeCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
    
    // Episode selection in player
    const episodeItems = document.querySelectorAll('.episode-item');
    if (episodeItems.length > 0) {
        episodeItems.forEach(item => {
            item.addEventListener('click', function() {
                episodeItems.forEach(i => i.classList.remove('active'));
                this.classList.add('active');
                // In a real app, this would load the selected episode
                loadEpisode(this.dataset.episodeId);
            });
        });
    }
    
    // Simulated functions for demo purposes
    function getSearchSuggestions(query) {
        // This would be replaced with an actual API call
        const allAnime = [
            { id: 1, title: 'Attack on Titan', type: 'Anime' },
            { id: 2, title: 'Demon Slayer', type: 'Anime' },
            { id: 3, title: 'Jujutsu Kaisen', type: 'Anime' },
            { id: 4, title: 'One Piece', type: 'Anime' },
            { id: 5, title: 'Naruto', type: 'Anime' },
            { id: 6, title: 'Death Note', type: 'Manga' },
            { id: 7, title: 'Tokyo Revengers', type: 'Manga' },
        ];
        
        return allAnime.filter(anime => 
            anime.title.toLowerCase().includes(query.toLowerCase())
        );
    }
    
    function displaySuggestions(suggestions) {
        if (suggestions.length === 0) {
            searchSuggestions.innerHTML = '<div class="suggestion-item">No results found</div>';
            searchSuggestions.style.display = 'block';
            return;
        }
        
        searchSuggestions.innerHTML = '';
        suggestions.forEach(item => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.textContent = `${item.title} (${item.type})`;
            div.dataset.id = item.id;
            div.addEventListener('click', function() {
                // In a real app, this would navigate to the item's page
                window.location.href = `/anime/${this.dataset.id}`;
            });
            searchSuggestions.appendChild(div);
        });
        
        searchSuggestions.style.display = 'block';
    }
    
    function loadEpisode(episodeId) {
        console.log(`Loading episode ${episodeId}`);
        // In a real app, this would update the video player source
    }
    
    // User dropdown functionality
    const userProfile = document.querySelector('.user-profile');
    if (userProfile) {
        userProfile.addEventListener('click', function(e) {
            e.stopPropagation();
            const dropdown = this.querySelector('.dropdown-content');
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        });
    }
    
    // Close dropdown when clicking anywhere else
    document.addEventListener('click', function() {
        const dropdowns = document.querySelectorAll('.dropdown-content');
        dropdowns.forEach(dropdown => {
            dropdown.style.display = 'none';
        });
    });
});