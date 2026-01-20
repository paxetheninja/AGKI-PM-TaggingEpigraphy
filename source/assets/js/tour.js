/**
 * AGKI Onboarding Tour
 * Uses Intro.js for guided walkthroughs of key features
 */

const TOUR_VERSION = '1.0';

// Check if user has completed tour
function hasTourCompleted(page) {
    const completed = localStorage.getItem(`agki_tour_${page}`);
    return completed === TOUR_VERSION;
}

// Mark tour as completed
function setTourCompleted(page) {
    localStorage.setItem(`agki_tour_${page}`, TOUR_VERSION);
}

// Reset all tours (for testing)
function resetAllTours() {
    ['index', 'search', 'explore', 'detail'].forEach(page => {
        localStorage.removeItem(`agki_tour_${page}`);
    });
    alert('Tours reset. Refresh the page to see the tour again.');
}

// Show tour prompt
function showTourPrompt(page, tourSteps) {
    if (hasTourCompleted(page)) return;

    // Create prompt overlay
    const prompt = document.createElement('div');
    prompt.id = 'tourPrompt';
    prompt.innerHTML = `
        <div class="tour-prompt-overlay">
            <div class="tour-prompt-box">
                <h3>Welcome to AGKI!</h3>
                <p>Would you like a quick tour of this page's features?</p>
                <div class="tour-prompt-buttons">
                    <button class="btn tour-start-btn" onclick="startTour('${page}')">Yes, show me around</button>
                    <button class="btn tour-skip-btn" onclick="skipTour('${page}')">Skip tour</button>
                </div>
                <label class="tour-dont-show">
                    <input type="checkbox" id="dontShowAgain"> Don't show this again
                </label>
            </div>
        </div>
    `;
    document.body.appendChild(prompt);

    // Add styles
    addTourStyles();
}

function addTourStyles() {
    if (document.getElementById('tourStyles')) return;

    const styles = document.createElement('style');
    styles.id = 'tourStyles';
    styles.textContent = `
        .tour-prompt-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        }
        .tour-prompt-box {
            background: var(--panel, #fff);
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            max-width: 400px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            border: 1px solid var(--border, #ddd);
        }
        .tour-prompt-box h3 {
            margin: 0 0 0.5rem;
            color: var(--primary, #c1683c);
        }
        .tour-prompt-box p {
            margin: 0 0 1.5rem;
            color: var(--text, #333);
        }
        .tour-prompt-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-bottom: 1rem;
        }
        .tour-start-btn {
            background: var(--primary, #c1683c) !important;
            color: white !important;
            border: none !important;
            padding: 0.6rem 1.2rem !important;
            border-radius: 4px !important;
            cursor: pointer !important;
        }
        .tour-skip-btn {
            background: var(--bg, #f5f5f5) !important;
            border: 1px solid var(--border, #ddd) !important;
            color: var(--text, #333) !important;
            padding: 0.6rem 1.2rem !important;
            border-radius: 4px !important;
            cursor: pointer !important;
        }
        .tour-skip-btn:hover {
            background: var(--panel, #fff) !important;
        }
        .tour-dont-show {
            font-size: 0.85rem;
            color: var(--muted, #666);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .tour-dont-show input {
            margin-right: 0.5rem;
        }

        /* Tour button in header */
        .tour-help-btn {
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.2);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            color: #fff;
            margin-right: 0.75rem;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
        }
        .tour-help-btn::before {
            content: "?";
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            background: #fff;
            color: var(--primary, #c1683c);
            border-radius: 50%;
            font-size: 0.75rem;
            font-weight: bold;
        }
        .tour-help-btn:hover {
            background: rgba(255,255,255,0.25);
            color: #fff;
            border-color: rgba(255,255,255,0.3);
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        .tour-help-btn:hover::before {
            background: #fff;
            color: var(--primary, #c1683c);
        }
        [data-theme="dark"] .tour-help-btn {
            background: rgba(255,255,255,0.15);
            border-color: rgba(255,255,255,0.2);
            color: #fff;
        }
        [data-theme="dark"] .tour-help-btn:hover {
            background: rgba(255,255,255,0.25);
            border-color: rgba(255,255,255,0.3);
            color: #fff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.4);
        }

        /* Intro.js dark mode overrides */
        [data-theme="dark"] .introjs-tooltip {
            background: var(--panel, #1e1e1e) !important;
            color: var(--text, #e0e0e0) !important;
            border: 1px solid var(--border, #333) !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
        }
        [data-theme="dark"] .introjs-tooltiptext {
            color: var(--text, #e0e0e0) !important;
        }
        [data-theme="dark"] .introjs-tooltip-title {
            color: var(--primary, #c1683c) !important;
        }
        [data-theme="dark"] .introjs-arrow.top,
        [data-theme="dark"] .introjs-arrow.top-right,
        [data-theme="dark"] .introjs-arrow.top-middle {
            border-bottom-color: var(--panel, #1e1e1e) !important;
        }
        [data-theme="dark"] .introjs-arrow.bottom,
        [data-theme="dark"] .introjs-arrow.bottom-right,
        [data-theme="dark"] .introjs-arrow.bottom-middle {
            border-top-color: var(--panel, #1e1e1e) !important;
        }
        [data-theme="dark"] .introjs-arrow.left,
        [data-theme="dark"] .introjs-arrow.left-bottom {
            border-right-color: var(--panel, #1e1e1e) !important;
        }
        [data-theme="dark"] .introjs-arrow.right,
        [data-theme="dark"] .introjs-arrow.right-bottom {
            border-left-color: var(--panel, #1e1e1e) !important;
        }
        [data-theme="dark"] .introjs-button {
            background: var(--bg, #121212) !important;
            color: var(--text, #e0e0e0) !important;
            border: 1px solid var(--border, #333) !important;
            text-shadow: none !important;
        }
        [data-theme="dark"] .introjs-button:hover {
            background: var(--panel, #1e1e1e) !important;
        }
        [data-theme="dark"] .introjs-button:focus {
            box-shadow: 0 0 0 2px var(--primary, #c1683c) !important;
        }
        [data-theme="dark"] .introjs-skipbutton {
            color: var(--muted, #888) !important;
        }
        [data-theme="dark"] .introjs-progress {
            background: var(--bg, #121212) !important;
        }
        [data-theme="dark"] .introjs-progressbar {
            background: var(--primary, #c1683c) !important;
        }
        [data-theme="dark"] .introjs-helperLayer {
            background: transparent !important;
            border: 2px solid var(--primary, #c1683c) !important;
            box-shadow: 0 0 0 9999px rgba(0,0,0,0.7) !important;
        }
        [data-theme="dark"] .introjs-bullets ul li a {
            background: var(--border, #333) !important;
        }
        [data-theme="dark"] .introjs-bullets ul li a.active {
            background: var(--primary, #c1683c) !important;
        }
    `;
    document.head.appendChild(styles);
}

function closeTourPrompt() {
    const prompt = document.getElementById('tourPrompt');
    if (prompt) prompt.remove();
}

function skipTour(page) {
    const dontShow = document.getElementById('dontShowAgain')?.checked;
    if (dontShow) {
        setTourCompleted(page);
    }
    closeTourPrompt();
}

function startTour(page) {
    closeTourPrompt();
    setTourCompleted(page);

    const steps = getTourSteps(page);
    if (!steps || steps.length === 0) return;

    introJs().setOptions({
        steps: steps,
        showProgress: true,
        showBullets: true,
        exitOnOverlayClick: false,
        disableInteraction: false,
        scrollToElement: true,
        scrollPadding: 80,
        tooltipClass: 'agki-intro-tooltip',
        highlightClass: 'agki-intro-highlight'
    }).start();
}

function getTourSteps(page) {
    const tours = {
        'index': [
            {
                title: 'Welcome to AGKI',
                intro: 'This is the home page of the AGKI Tagging Tool. It provides an overview of the entire epigraphic corpus with key statistics and visualizations.'
            },
            {
                element: '.hero-stats',
                title: 'Corpus Statistics',
                intro: 'These cards show key metrics about the inscription corpus: total inscriptions, unique entities, and thematic tags.'
            },
            {
                element: '.nav-links',
                title: 'Navigation',
                intro: 'Use these links to navigate between different views: Search for specific inscriptions, Explore with filters and maps, Compare regions, and browse Indices.'
            },
            {
                element: '.theme-toggle-btn',
                title: 'Dark Mode',
                intro: 'Toggle between light and dark themes for comfortable reading.'
            }
        ],
        'search': [
            {
                title: 'Search Inscriptions',
                intro: 'This page lets you search through the corpus using full-text search across inscription texts and metadata.'
            },
            {
                element: '#searchInput',
                title: 'Search Box',
                intro: 'Type your search query here. You can search for Greek text, names, places, keywords, or standard publication references (e.g., "IG II²").'
            },
            {
                element: '#entityType',
                title: 'Entity Filter',
                intro: 'Filter results by entity type: show only inscriptions mentioning persons, places, or deities.'
            },
            {
                element: '#roleSelect',
                title: 'Role Filter',
                intro: 'Filter by person roles like "priest", "magistrate", or "dedicant" to find specific social roles.'
            },
            {
                element: '#regionSelect',
                title: 'Region Filter',
                intro: 'Narrow results to a specific geographic region like Attica, Boeotia, or Macedonia.'
            }
        ],
        'explore': [
            {
                title: 'Explore the Corpus',
                intro: 'This is the main exploration interface with advanced filtering, timeline visualization, and interactive map.'
            },
            {
                element: '#taxonomyFilters',
                title: 'Taxonomy Filters',
                intro: 'Filter inscriptions by thematic tags. Click tags to include them (green) or exclude them (red). Use the toggle to switch between modes.'
            },
            {
                element: '#regionFilter',
                title: 'Region Filter',
                intro: 'Filter by geographic region. You can also click on the map to filter by location.'
            },
            {
                element: '#myCollectionList',
                title: 'My Collection',
                intro: 'Inscriptions you "star" will appear here for quick access. You can export this list.'
            },
            {
                element: '#queryExplanation',
                title: 'Query Explanation',
                intro: 'This banner shows a natural language summary of your current filters, making it easy to understand what you\'re viewing.'
            },
            {
                element: '#mapContainer',
                title: 'Interactive Map',
                intro: 'Click markers to view inscriptions. Click on a region polygon to automatically filter the results to that region.'
            },
            {
                element: '.viz-row',
                title: 'Key Statistics',
                intro: 'See breakdowns of Completeness (intact vs. fragmentary) and the most frequently mentioned Deities and Places.'
            },
            {
                element: '#timeChart',
                title: 'Timeline',
                intro: 'This chart shows the temporal distribution of your filtered results. It updates as you apply filters.'
            },
            {
                element: '#sankeyChart',
                title: 'Thematic Flows',
                intro: 'Trace how themes are distributed across different regions.'
            },
            {
                element: '#heatmapChart',
                title: 'Thematic Heatmap',
                intro: 'Identify "hotspots" where specific themes appear most frequently.'
            }
        ],
        'detail': [
            {
                title: 'Inscription Detail',
                intro: 'This page shows the full details of a single inscription, including the Greek text, AI-generated tags, and metadata.'
            },
            {
                element: '.inscription-meta',
                title: 'Metadata',
                intro: 'Key information including Provenance, Date, Completeness, and the AI Model version used for tagging.'
            },
            {
                element: '.greek-content',
                title: 'Greek Text',
                intro: 'The original Greek inscription text. Line numbers on the left help with citations. Hover over highlighted sections to see tag evidence.'
            },
            {
                element: '.theme-card',
                title: 'Thematic Tags',
                intro: 'AI-generated tags with confidence scores. Look for the "⚠️ Ambiguous" badge, which flags cases where the AI found conflicting categories.'
            },
            {
                element: '#reportBtn',
                title: 'Report Errors',
                intro: 'Found a mistake? Click here to report tagging errors or suggest corrections.'
            },
            {
                element: '#citeBtn',
                title: 'Citation',
                intro: 'Copy a formatted citation for this inscription to use in your research.'
            }
        ],
        'compare': [
            {
                title: 'Regional Comparison',
                intro: 'Compare inscription characteristics across different geographic regions to identify regional patterns and differences.'
            },
            {
                element: '#regionSelector',
                title: 'Select Regions',
                intro: 'Choose multiple regions to compare. The visualizations will update to show differences and similarities between your selected regions.'
            },
            {
                element: '.comparison-charts',
                title: 'Comparison Charts',
                intro: 'These charts show side-by-side comparisons of theme distribution, completeness, and temporal patterns across regions.'
            },
            {
                element: '.theme-toggle-btn',
                title: 'Dark Mode',
                intro: 'Toggle between light and dark themes for comfortable viewing of the comparison data.'
            }
        ],
        'network': [
            {
                title: 'Prosopography Network',
                intro: 'Visualize relationships between persons, deities, and places mentioned together in inscriptions.'
            },
            {
                element: '#networkGraph',
                title: 'Network Graph',
                intro: 'This force-directed graph shows connections between entities. Nodes represent persons/deities/places, and edges show co-occurrences in inscriptions.'
            },
            {
                element: '#entityTypeFilter',
                title: 'Entity Type Filter',
                intro: 'Filter the network to show only specific types of entities: persons, deities, or places.'
            },
            {
                element: '#minConnectionsSlider',
                title: 'Connection Threshold',
                intro: 'Adjust this slider to show only entities with a minimum number of connections, reducing clutter in the visualization.'
            },
            {
                element: '.network-legend',
                title: 'Legend',
                intro: 'Node colors indicate entity types: orange for persons, teal for places, and purple for deities.'
            }
        ],
        'matrix': [
            {
                title: 'Tag Co-occurrence Matrix',
                intro: 'Explore which thematic tags frequently appear together in inscriptions using this interactive heatmap.'
            },
            {
                element: '.matrix-table',
                title: 'Co-occurrence Matrix',
                intro: 'Each cell shows how often two tags appear together. Darker colors indicate stronger associations. Hover over cells for exact counts.'
            },
            {
                element: '#matrixLevel',
                title: 'Hierarchy Level',
                intro: 'Switch between top-level categories and more detailed subcategories to explore patterns at different granularities.'
            },
            {
                element: '#minOccurrence',
                title: 'Minimum Occurrence',
                intro: 'Filter out rare tag combinations by setting a minimum co-occurrence threshold.'
            },
            {
                element: '.theme-toggle-btn',
                title: 'Dark Mode',
                intro: 'Toggle between light and dark themes. The matrix colors adjust automatically for optimal contrast.'
            }
        ]
    };

    return tours[page] || [];
}

// Add help button to page
function addTourButton(page) {
    addTourStyles();

    // Find header controls
    const controls = document.querySelector('.header-controls');
    if (!controls) return;

    // Check if button already exists
    if (document.querySelector('.tour-help-btn')) return;

    const btn = document.createElement('button');
    btn.className = 'tour-help-btn';
    btn.innerHTML = 'Tour';
    btn.onclick = () => startTour(page);
    controls.insertBefore(btn, controls.firstChild);
}

// Initialize tour on page load
function initTour(page) {
    // Add help button
    addTourButton(page);

    // Show prompt for first-time visitors
    setTimeout(() => {
        showTourPrompt(page, getTourSteps(page));
    }, 1000);
}

// Export for use in pages
window.AGKI_Tour = {
    init: initTour,
    start: startTour,
    reset: resetAllTours
};
