import scrapy
import json
import asyncio
import threading
import time
import re
import math
import os
from datetime import datetime, timedelta
from urllib.parse import quote_plus, urlparse, parse_qs
from scrapy_playwright.page import PageMethod
from business_scraper.utils.performance_analyzer import PerformanceAnalyzer
from business_scraper.items import FuelStationItem

class FuelStationsSpider(scrapy.Spider):
    name = 'fuel_stations'
    allowed_domains = ['google.com']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Thread safety locks
        self.results_lock = threading.Lock()
        self.file_lock = threading.Lock()
        self.progress_lock = threading.Lock()
        
        # Data storage
        self.seen_place_ids = set()
        self.results = []
        self.establishments_processed = 0
        self.cells_processed = 0
        
        # Performance tracking
        self.performance_analyzer = PerformanceAnalyzer()
        self.start_time = time.time()
        self.last_pause_time = time.time()
        self.last_long_pause_time = time.time()
        
        # Grid configuration for Santa Catarina
        self.lat_min = -29.35
        self.lat_max = -25.95
        self.lon_min = -53.83
        self.lon_max = -48.35
        self.grid_size_km = 5
        
        # Search terms (optimized for fuel stations)
        self.search_terms = [
            "gas station",  # English term, official Google category
            "posto de combustível"  # Portuguese term, common usage
        ]
        
        # Blocking detection
        self.blocked = False
        self.block_count = 0
        
        # Create output directory
        os.makedirs('output', exist_ok=True)
        
        # Load checkpoint if exists
        self.checkpoint = self.performance_analyzer.load_checkpoint()
        self.start_cell_index = self.checkpoint.get('last_cell_index', 0)
        
        self.logger.info(f"Starting from cell index: {self.start_cell_index}")

    def start_requests(self):
        """Generate initial requests for the grid search"""
        grid_cells = self._generate_grid_cells()
        self.performance_analyzer.update_total_cells(len(grid_cells))
        
        self.logger.info(f"Generated {len(grid_cells)} grid cells for scraping")
        
        # Start from checkpoint if resuming
        for i, (lat, lon, term) in enumerate(grid_cells):
            if i < self.start_cell_index:
                continue
                
            url = f"https://www.google.com/maps/search/{quote_plus(term)}/@{lat},{lon},14z"
            
            yield scrapy.Request(
                url=url,
                callback=self.parse_search_results,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', 'div[role="feed"]', timeout=15000),
                    ],
                    'cell_index': i,
                    'lat': lat,
                    'lon': lon,
                    'term': term,
                    'max_scrolls': 10
                },
                dont_filter=True
            )

    def _generate_grid_cells(self):
        """Generate grid cells for Santa Catarina with 5km spacing"""
        cells = []
        
        # Calculate grid steps
        lat_step = self.grid_size_km / 111.0  # 1 degree lat ≈ 111 km
        
        # Longitude step adjusted for latitude (cos correction)
        avg_lat = (self.lat_min + self.lat_max) / 2
        lon_step = self.grid_size_km / (111.0 * math.cos(math.radians(avg_lat)))
        
        # Generate grid points
        lat = self.lat_min
        while lat <= self.lat_max:
            lon = self.lon_min
            while lon <= self.lon_max:
                # Add both search terms for each cell
                for term in self.search_terms:
                    cells.append((lat, lon, term))
                lon += lon_step
            lat += lat_step
        
        self.logger.info(f"Generated {len(cells)} total searches ({len(cells)//2} cells × 2 terms)")
        return cells

    def parse_search_results(self, response):
        """Parse search results from Google Maps list view"""
        cell_index = response.meta['cell_index']
        lat = response.meta['lat']
        lon = response.meta['lon']
        term = response.meta['term']
        max_scrolls = response.meta.get('max_scrolls', 10)
        
        self.performance_analyzer.start_cell_processing(cell_index, lat, lon, term)
        
        # Check for blocking
        if self._is_blocked(response):
            self.logger.warning(f"Blocking detected for cell {cell_index}")
            self.performance_analyzer.report_block_detected()
            self._handle_blocking()
            self.performance_analyzer.complete_cell_processing(cell_index, 0, False, "Blocked")
            return
        
        # Use Playwright page methods for async operations
        return response.follow_all(
            [],  # No URLs to follow
            callback=self._process_page_async,
            meta={
                **response.meta,
                'playwright': True,
                'playwright_page_methods': [
                    PageMethod('wait_for_selector', 'div[role="feed"]', timeout=15000),
                    PageMethod('evaluate', '''
                        async () => {
                            const scrollAndExtract = async () => {
                                let establishments = [];
                                let scrollCount = 0;
                                const maxScrolls = 10;

                                while (scrollCount < maxScrolls) {
                                    // Get current cards
                                    const cards = document.querySelectorAll('div[data-result-index]');

                                    for (const card of cards) {
                                        try {
                                            const data = {};

                                            // Extract name
                                            const nameSelectors = ['div.fontHeadlineSmall', 'a.hfpxzc', 'div.qBF1Pd'];
                                            for (const selector of nameSelectors) {
                                                const nameEl = card.querySelector(selector);
                                                if (nameEl) {
                                                    data.name = nameEl.innerText;
                                                    break;
                                                }
                                            }

                                            if (!data.name) continue;

                                            // Extract rating
                                            const ratingEl = card.querySelector('span.MW4etd');
                                            if (ratingEl) {
                                                try {
                                                    data.rating = parseFloat(ratingEl.innerText.replace(',', '.'));
                                                } catch (e) {
                                                    data.rating = null;
                                                }
                                            }

                                            // Extract reviews
                                            const reviewsEl = card.querySelector('span.UY7F9');
                                            if (reviewsEl) {
                                                const reviewsMatch = reviewsEl.innerText.match(/\\((\\d+)\\)/);
                                                data.reviews_count = reviewsMatch ? parseInt(reviewsMatch[1]) : null;
                                            }

                                            // Extract category
                                            const categoryEl = card.querySelector('div.W4Efsd span');
                                            if (categoryEl) {
                                                data.category = categoryEl.innerText;
                                            }

                                            // Extract address
                                            const addressEls = card.querySelectorAll('div.W4Efsd');
                                            for (const el of addressEls) {
                                                const text = el.innerText;
                                                if (/\\d+|rua|av|avenida|street|st\\.|road|rd\\./i.test(text)) {
                                                    data.address = text;
                                                    break;
                                                }
                                            }

                                            // Extract link and place_id
                                            const linkEl = card.querySelector('a.hfpxzc');
                                            if (linkEl && linkEl.href) {
                                                data.link = linkEl.href;
                                                const placeMatch = linkEl.href.match(/place\\/([^\\/]+)/);
                                                if (placeMatch) {
                                                    data.place_id = placeMatch[1];
                                                } else {
                                                    const altMatch = linkEl.href.match(/data=.*?1s([^!]+)/);
                                                    if (altMatch) {
                                                        data.place_id = altMatch[1];
                                                    }
                                                }
                                            }

                                            if (!data.place_id) {
                                                data.place_id = (data.name + '_' + (data.address || '')).replace(/[^\\w\\s-]/g, '').replace(/\\s+/g, '_');
                                            }

                                            // Add metadata
                                            data.scraped_at = new Date().toISOString();
                                            data.source = 'google_maps_list';

                                            // Validate fuel station
                                            const nameL = data.name.toLowerCase();
                                            const categoryL = (data.category || '').toLowerCase();
                                            const fuelKeywords = ['posto', 'gas', 'petrol', 'combustível', 'gasolina', 'shell', 'br', 'ipiranga', 'esso', 'texaco', 'ale', 'station', 'fuel', 'diesel', 'etanol', 'gnv'];

                                            if (fuelKeywords.some(k => nameL.includes(k) || categoryL.includes(k))) {
                                                establishments.push(data);
                                            }

                                        } catch (e) {
                                            console.log('Error extracting card:', e);
                                        }
                                    }

                                    // Check for end of results
                                    const endMessages = ['Você chegou ao fim', "You've reached the end", 'Fim dos resultados', 'No more results'];
                                    if (endMessages.some(msg => document.body.innerText.includes(msg))) {
                                        break;
                                    }

                                    // Scroll down
                                    window.scrollTo(0, document.body.scrollHeight);
                                    await new Promise(resolve => setTimeout(resolve, 2000));
                                    scrollCount++;
                                }

                                return establishments;
                            };

                            return await scrollAndExtract();
                        }
                    ''')
                ]
            }
        )

    def _process_page_async(self, response):
        """Process the async page results"""
        cell_index = response.meta['cell_index']
        lat = response.meta['lat']
        lon = response.meta['lon']
        term = response.meta['term']

        try:
            # Get results from JavaScript execution
            establishments_data = response.meta.get('playwright_page_result', [])
            establishments_found = 0

            for data in establishments_data:
                if self._add_unique_establishment(data):
                    establishments_found += 1

                    # Create and yield item
                    item = FuelStationItem()
                    for key, value in data.items():
                        if key in item.fields:
                            item[key] = value
                    yield item

                    # Save incrementally every 50 items
                    if len(self.results) % 50 == 0:
                        self._save_incremental_results()

            self.performance_analyzer.complete_cell_processing(cell_index, establishments_found, True)

            # Save checkpoint every 10 cells
            if cell_index % 10 == 0:
                self.performance_analyzer.save_checkpoint(cell_index)

            # Implement programmed pauses
            self._check_programmed_pauses()

        except Exception as e:
            self.logger.error(f"Error processing cell {cell_index}: {str(e)}")
            self.performance_analyzer.complete_cell_processing(cell_index, 0, False, str(e))



    def _add_unique_establishment(self, data):
        """Add establishment if not duplicate (thread-safe)"""
        with self.results_lock:
            place_id = data['place_id']
            if place_id not in self.seen_place_ids:
                self.seen_place_ids.add(place_id)
                self.results.append(data)
                self.establishments_processed += 1
                self.performance_analyzer.add_unique_establishment()
                return True
            else:
                self.performance_analyzer.add_duplicate_filtered()
                return False



    def _is_blocked(self, response):
        """Detect if we're being blocked by Google"""
        # Check status code
        if response.status == 429:
            return True

        # Check URL for captcha
        if 'captcha' in response.url.lower():
            return True

        # Check for blocking indicators in content
        content = response.text.lower()
        blocking_indicators = [
            'unusual traffic',
            'automated queries',
            'captcha',
            'blocked',
            'suspicious activity'
        ]

        return any(indicator in content for indicator in blocking_indicators)

    def _handle_blocking(self):
        """Handle blocking detection"""
        self.blocked = True
        self.block_count += 1

        if self.block_count >= 3:
            # Reduce concurrency permanently
            self.crawler.settings.set('CONCURRENT_REQUESTS', 1)
            self.crawler.settings.set('DOWNLOAD_DELAY', 8)
            self.logger.warning("Multiple blocks detected, reducing concurrency permanently")

        # Pause for 30 minutes
        self.logger.info("Pausing for 30 minutes due to blocking...")
        time.sleep(1800)  # 30 minutes
        self.blocked = False

    def _check_programmed_pauses(self):
        """Implement programmed pauses to avoid detection"""
        current_time = time.time()

        # Pause every 200 establishments (10 minutes)
        if self.establishments_processed > 0 and self.establishments_processed % 200 == 0:
            if current_time - self.last_pause_time > 3600:  # At least 1 hour since last pause
                self.logger.info(f"Programmed pause: 200 establishments processed. Pausing for 10 minutes...")
                time.sleep(600)  # 10 minutes
                self.last_pause_time = current_time

        # Long pause every 8 hours
        if current_time - self.last_long_pause_time > 28800:  # 8 hours
            self.logger.info("Long programmed pause: 8 hours elapsed. Pausing for 1 hour...")
            time.sleep(3600)  # 1 hour
            self.last_long_pause_time = current_time

        # Regular pause every 3 hours
        elif current_time - self.last_pause_time > 10800:  # 3 hours
            self.logger.info("Regular programmed pause: 3 hours elapsed. Pausing for 15 minutes...")
            time.sleep(900)  # 15 minutes
            self.last_pause_time = current_time

    def _save_incremental_results(self):
        """Save results incrementally (thread-safe)"""
        with self.file_lock:
            try:
                output_file = 'output/fuel_stations.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, ensure_ascii=False, indent=2)

                self.logger.info(f"Saved {len(self.results)} establishments to {output_file}")

            except Exception as e:
                self.logger.error(f"Error saving incremental results: {str(e)}")

    def closed(self, reason):
        """Called when spider closes"""
        # Final save
        self._save_incremental_results()

        # Save final metrics
        summary = self.performance_analyzer.get_summary()

        self.logger.info("=" * 50)
        self.logger.info("SCRAPING COMPLETED")
        self.logger.info("=" * 50)
        self.logger.info(f"Total establishments found: {summary['unique_establishments']}")
        self.logger.info(f"Cells processed: {summary['cells_processed']}/{summary['total_cells']}")
        self.logger.info(f"Success rate: {summary['success_rate']:.1f}%")
        self.logger.info(f"Processing speed: {summary['processing_speed']:.2f} cells/hour")
        self.logger.info(f"Data quality score: {summary['data_quality_score']:.1f}%")
        self.logger.info(f"Total time: {summary['elapsed_time_hours']:.2f} hours")
        self.logger.info("=" * 50)

        # Save final checkpoint
        self.performance_analyzer.save_checkpoint(self.cells_processed)
