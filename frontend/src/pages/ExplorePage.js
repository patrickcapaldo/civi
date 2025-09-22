import React, { useRef, useEffect, useState, useMemo, useCallback } from 'react';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';
import { geoOrthographic, geoPath } from 'd3-geo';
import { Radar } from 'react-chartjs-2';
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js';
import LatexRenderer from '../LatexRenderer';
import 'katex/dist/katex.min.css';
import './ExplorePage.css';

const PILLARS = ["autonomy", "resilience", "sustainability", "effectiveness"];

const INDUSTRIES = [
    "communications",
    "defence",
    "energy",
    "finance",
    "food_agriculture",
    "healthcare",
    "transport",
    "water",
    "waste_management",
    "emergency_services",
    "information_technology",
];

// Register Chart.js components
ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const PillarScores = ({ pillarScores, industryIndicators }) => {
    const [expandedPillars, setExpandedPillars] = useState([]);

    const togglePillar = (pillar) => {
        setExpandedPillars(prevExpanded =>
            prevExpanded.includes(pillar)
                ? prevExpanded.filter(p => p !== pillar)
                : [...prevExpanded, pillar]
        );
    };

    if (!pillarScores) {
        return null;
    }

    return (
        <div className="pillar-scores-container">
            <h4>Pillar Score Calculation</h4>
            <div className="info-box note">
                <span className="symbol">🐨</span>
                <div>
                    Each pillar score is a weighted average of its underlying indicators.
                    <div className="formula-box">
                        <LatexRenderer displayMode={true}>{`$Pillar Score = \\frac{\\sum_{i=1}^{N} (I_i \\times W_i)}{\\sum_{i=1}^{N} W_i}$`}</LatexRenderer>
                    </div>
                </div>
            </div>

            <div className="pillar-cards">
                {PILLARS.map(pillar => {
                    const score = pillarScores[pillar];
                    const confidenceScore = pillarScores[`${pillar}_confidence`];
                    const indicatorsForPillar = industryIndicators.filter(i => i.pillar === pillar && i.value !== null);
                    const hasScore = score !== null && score !== undefined;

                    return (
                        <div key={pillar} className="pillar-card" onClick={() => togglePillar(pillar)}>
                            <div className="pillar-card-header">
                                <h5>{pillar.charAt(0).toUpperCase() + pillar.slice(1)}</h5>
                                <div className="pillar-scores">
                                    <span>Score: {hasScore ? score.toFixed(2) : 'No data'}</span>
                                    <span>Confidence: {confidenceScore !== undefined ? `${(confidenceScore * 100).toFixed(0)}%` : 'N/A'}</span>
                                </div>
                            </div>
                            {expandedPillars.includes(pillar) && hasScore && (
                                <div className="pillar-card-body">
                                    <table className="sub-indicators-table">
                                        <thead>
                                            <tr>
                                                <th>Variable</th>
                                                <th>Indicator Description</th>
                                                <th>Value</th>
                                                <th>Weight</th>
                                                <th>Source</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {indicatorsForPillar.map((indicator, index) => (
                                                <tr key={indicator.key}>
                                                    <td><LatexRenderer>{`$I_{${index + 1}}$`}</LatexRenderer></td>
                                                    <td>{indicator.description}</td>
                                                    <td>{indicator.value !== null ? indicator.value.toFixed(2) : 'N/A'}</td>
                                                    <td><LatexRenderer>{`$W_{${index + 1}}$`}</LatexRenderer></td>
                                                    <td>{indicator.source}{indicator.year ? `, ${indicator.year}` : ''}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

const IndustryRadarChart = ({ industryKey, industryName, civiData, selectedCountry }) => { // Removed getIndustryRadarData from props, added selectedCountry
    const industryData = getIndustryRadarData(selectedCountry, civiData, industryKey); // Call external helper
    const industryIndicators = civiData?.industries[industryKey]?.indicators;
    const pillarScores = civiData?.industries[industryKey]?.scores;

    const errorBarsPlugin = {
        id: 'errorBars',
        afterDraw: (chart) => {
            const ctx = chart.ctx;
            const meta = chart.getDatasetMeta(0);
            const scale = chart.scales.r;

            meta.data.forEach((point, index) => {
                const confidence = chart.data.datasets[0].confidence[index];
                if (confidence === undefined || confidence === null) return;

                const score = chart.data.datasets[0].data[index];
                if (score === null || score === undefined) return;

                const error = (1 - confidence) * score * 0.1; // 10% of the score on each side

                const angle = Math.atan2(point.y - scale.yCenter, point.x - scale.xCenter);

                const x1 = point.x - error * Math.cos(angle);
                const y1 = point.y - error * Math.sin(angle);
                const x2 = point.x + error * Math.cos(angle);
                const y2 = point.y + error * Math.sin(angle);

                ctx.save();
                ctx.strokeStyle = 'rgba(255, 0, 0, 0.8)';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.stroke();
                ctx.restore();
            });
        }
    };
    
    return (        <div>
            <h3>{industryName} Details</h3>
            <div className="chart-container">
                {industryData ? <Radar data={{ labels: industryData.labels, datasets: industryData.datasets }} options={industryData.options} plugins={[errorBarsPlugin]} width={400} height={400} /> : <p>Data not available for {industryName}.</p>}
            </div>
            {industryIndicators && (
                <div style={{ marginTop: '20px' }}>
                    <PillarScores pillarScores={pillarScores} industryIndicators={industryIndicators} />
                </div>
            )}
        </div>
    );
};

const getIndustryRadarData = (selectedCountry, civiData, industryKey) => {
      if (!selectedCountry || !civiData || !civiData.industries || !civiData.industries[industryKey] || !civiData.industries[industryKey].scores) return null;

      const countryData = civiData;
      const industryData = countryData.industries[industryKey];
      const scores = industryData.scores;

      const data = PILLARS.map(p => scores[p]);
      const confidence = PILLARS.map(p => scores[`${p}_confidence`]);

      return {
          labels: ['Autonomy', 'Resilience', 'Sustainability', 'Effectiveness'],
          datasets: [{
              label: 'Score',
              data: data,
              confidence: confidence, // Pass confidence scores to the plugin
              borderColor: 'rgba(0, 150, 136, 1)',
              backgroundColor: 'rgba(0, 150, 136, 0.2)',
              borderWidth: 1,
          }],
          options: {
              animation: false,
              responsive: false, // Disable responsiveness
              responsiveAnimationDuration: 0, // Disable responsive animation
              scales: {
                  r: {
                      min: 0,
                      max: 100,
                      ticks: {
                          stepSize: 20,
                          callback: function(value, index, values) {
                              if ([20, 40, 60, 80, 100].includes(value)) {
                                  return value;
                              }
                              return null;
                          }
                      }
                  }
              }
          }
      };
  }; // Closing brace for getIndustryRadarData

const ExplorePage = ({ headerHeight }) => {
  const svgRef = useRef();
  const tooltipRef = useRef();
  const [worldData, setWorldData] = useState(null);
  const [civiData, setCiviData] = useState(null);
  const [countryCodeMap, setCountryCodeMap] = useState(null);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [activeTab, setActiveTab] = useState('Overview');
  const [windowDimensions, setWindowDimensions] = useState({ width: window.innerWidth, height: window.innerHeight });
  const [showFilters, setShowFilters] = useState(false);
  const [selectedFilterType, setSelectedFilterType] = useState('Overall Score'); // 'Overall Score' or 'Industry Score'
  const [selectedIndustryFilter, setSelectedIndustryFilter] = useState(null); // e.g., 'energy', 'communications'
  const [selectedPillarFilter, setSelectedPillarFilter] = useState(null); // e.g., 'autonomy', 'resilience'
  const [colorScheme, setColorScheme] = useState('Green-Yellow-Red'); // e.g., 'Green-Yellow-Red'
  const [allCiviData, setAllCiviData] = useState({}); // Stores all civi data by alpha3 code

  const getCountryScore = useCallback((countryAlpha3, filterType, industryFilter) => {
    const countryData = allCiviData[countryAlpha3];
    if (!countryData) return null;

    if (filterType === 'Overall Score') {
      const scores = countryData.scores;
      if (!scores) return null;
      const pillarScores = PILLARS.map(pillar => scores[pillar]).filter(score => score !== null && score !== undefined);
      if (pillarScores.length === 0) return null;
      return pillarScores.reduce((sum, score) => sum + score, 0) / pillarScores.length;
    } else if (filterType === 'Industry Score' && industryFilter) {
      const industryPillarScores = countryData.industries?.[industryFilter]?.scores;
      if (!industryPillarScores) return null;
      const scoresForIndustry = PILLARS.map(pillar => industryPillarScores[pillar]).filter(score => score !== null && score !== undefined);
      if (scoresForIndustry.length === 0) return null;
      return scoresForIndustry.reduce((sum, score) => sum + score, 0) / scoresForIndustry.length;
    } else if (filterType === 'Pillar Score' && selectedPillarFilter) {
      const scores = countryData.scores;
      if (!scores) return null;
      return scores[selectedPillarFilter];
    }
    return null;
  }, [allCiviData, selectedFilterType, selectedIndustryFilter, selectedPillarFilter]);

  const getColorScale = useMemo(() => {
    // Define the color scale based on the selected colorScheme
    if (colorScheme === 'Green-Yellow-Red') {
      return d3.scaleLinear()
        .domain([0, 50, 100]) // Scores from 0 to 100
        .range(['red', 'yellow', 'green']); // Red for low, Yellow for mid, Green for high
    }
    // Default color scale if others are added
    return d3.scaleLinear()
      .domain([0, 100])
      .range(['lightgray', 'darkgray']);
  }, [colorScheme]);

  const [projection] = useState(() => 
    geoOrthographic().clipAngle(90)
  );

  // Fetch initial data sources (world map and country codes)
  useEffect(() => {
    Promise.all([
      d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json'),
      d3.json('./country-codes.json')
    ]).then(([world, codes]) => {
      setWorldData(topojson.feature(world, world.objects.countries));
      const codeMap = codes.reduce((acc, d) => {
        const numericId = parseInt(d['country-code'], 10);
        acc[numericId] = d['alpha-3'];
        return acc;
      }, {});
      setCountryCodeMap(codeMap);
    }).catch(error => console.error("Error loading initial data:", error));
  }, []);

  // Effect to fetch all country data once countryCodeMap is available
  useEffect(() => {
    if (countryCodeMap && Object.keys(countryCodeMap).length > 0) {
      const fetchPromises = Object.values(countryCodeMap).map(alpha3 =>
        d3.json(`/civi_modular/${alpha3}.json`)
          .then(data => ({ [alpha3]: data }))
          .catch(error => {
            console.error(`Error loading data for ${alpha3}:`, error);
            return { [alpha3]: null }; // Return null for failed fetches
          })
      );

      Promise.all(fetchPromises)
        .then(results => {
          const combinedData = results.reduce((acc, curr) => ({ ...acc, ...curr }), {});
          setAllCiviData(combinedData);
        });
    }
  }, [countryCodeMap]);

  // Effect to set civiData for the selected country from allCiviData
  useEffect(() => {
    if (selectedCountry && countryCodeMap && allCiviData) {
      const alpha3 = countryCodeMap[selectedCountry.id];
      if (alpha3 && allCiviData[alpha3]) {
        setCiviData(allCiviData[alpha3]);
      }
    } else {
      setCiviData(null);
    }
  }, [selectedCountry, countryCodeMap, allCiviData]);

  // Effect for window resize
  useEffect(() => {
    const handleResize = () => {
      setWindowDimensions({ width: window.innerWidth, height: window.innerHeight });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Main D3 rendering effect
  useEffect(() => {
    document.body.classList.add('explore-page-active');
    return () => {
      document.body.classList.remove('explore-page-active');
    };
  }, []);

  useEffect(() => {
    if (!worldData || !countryCodeMap || headerHeight === 0) return; // Wait for headerHeight

    const svgWidth = windowDimensions.width;
    const svgHeight = windowDimensions.height - headerHeight; // SVG height is remaining space

    // Calculate scale based on a percentage of the minimum available dimension within the SVG
    const scaleFactor = 0.45; // Adjust this value to control how much space the globe occupies
    const scale = Math.min(svgWidth, svgHeight) * scaleFactor;

    const translateX = svgWidth / 2;
    const translateY = svgHeight / 2; // Center within the SVG's height

    projection.scale(scale).translate([translateX, translateY]);

    const path = geoPath().projection(projection);
    const svg = d3.select(svgRef.current)
      .attr('width', svgWidth)
      .attr('height', svgHeight)
      .style('position', 'absolute')
      .style('top', `${headerHeight}px`)
      .style('left', '0px');

    const getAlpha3 = (d) => d && countryCodeMap[d.id];

    const tooltip = d3.select(tooltipRef.current);

    svg.selectAll('*').remove(); // Clear previous render

    // Draw countries
    const countryPaths = svg.append('g')
      .selectAll('path')
      .data(worldData.features)
      .enter()
      .append('path')
      .attr('d', path)
      .attr('class', 'country')
      .attr('fill', d => {
          const alpha3 = getAlpha3(d);
          if (selectedCountry === d) {
              return '#ff9800'; // Highlight selected country
          }
          if (selectedFilterType === 'No Filters') {
              return '#666'; // Default color when no filters are applied
          } else {
              if (!allCiviData[alpha3] || !allCiviData[alpha3].scores) {
                  return '#666'; // Default color for countries with no data
              }

              const score = getCountryScore(alpha3, selectedFilterType, selectedIndustryFilter);
              if (score === null) {
                  return '#ccc'; // Light gray for countries with data but no score for the current filter
              }
              return getColorScale(score);
          }
      })
      .attr('stroke', '#1a1a1a')
      .attr('stroke-width', 0.5);

    // Add Interactivity
    countryPaths
      .on('mouseover', (event, d) => {
        const currentTarget = d3.select(event.currentTarget);
        if (selectedCountry !== d) {
            // Store original stroke and stroke-width
            currentTarget.property('originalStroke', currentTarget.attr('stroke'));
            currentTarget.property('originalStrokeWidth', currentTarget.attr('stroke-width'));
            
            // Bring the hovered country to the front
            currentTarget.raise(); 
            
            // Apply the outline directly to the hovered country
            currentTarget.attr('stroke', '#87CEEB').attr('stroke-width', 4).attr('stroke-linejoin', 'round'); // SkyBlue outline
        }
        const countryName = civiData?.name || d.properties.name || 'N/A';
        tooltip
          .style('opacity', 1)
          .html(countryName);
      })
      .on('mousemove', (event) => {
        tooltip
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 20) + 'px');
      })
      .on('mouseout', (event, d) => {
        const currentTarget = d3.select(event.currentTarget);
        if (selectedCountry !== d) {
            // Revert to original stroke and stroke-width
            currentTarget.attr('stroke', currentTarget.property('originalStroke'));
            currentTarget.attr('stroke-width', currentTarget.property('originalStrokeWidth'));
            currentTarget.attr('stroke-linejoin', 'miter'); // Revert to default miter joins
        }
        tooltip.style('opacity', 0);
      })
      .on('click', (event, d) => {
        const alpha3 = getAlpha3(d);
        if (alpha3) {
            setSelectedCountry(selectedCountry === d ? null : d);
        }
      });

    // Implement smooth dragging
    const drag = d3.drag()
      .on('drag', (event) => {
        const rotate = projection.rotate();
        const sensitivity = 0.25; // Adjusted for smoother rotation
        const deltaX = event.dx * sensitivity;
        const deltaY = event.dy * sensitivity;
        projection.rotate([rotate[0] + deltaX, rotate[1] - deltaY]);
        svg.selectAll('path').attr('d', path);
      });

    svg.call(drag);

  }, [worldData, civiData, countryCodeMap, selectedCountry, headerHeight, windowDimensions, projection, getColorScale, selectedFilterType, selectedIndustryFilter, allCiviData, getCountryScore]);

  const handleCloseModal = () => setSelectedCountry(null);

  const getRadarData = () => {
      if (!selectedCountry || !civiData || !civiData.scores) return null;

      const countryData = civiData;

      return {
          labels: ['Autonomy', 'Resilience', 'Sustainability', 'Effectiveness'],
          datasets: [{
              label: countryData.name,
              data: [
                  countryData.scores.autonomy,
                  countryData.scores.resilience,
                  countryData.scores.sustainability,
                  countryData.scores.effectiveness,
              ],
              backgroundColor: 'rgba(255, 152, 0, 0.2)',
              borderColor: 'rgba(255, 152, 0, 1)',
              borderWidth: 1,
          }],
          options: {
              animation: false,
              responsive: false, // Disable responsiveness
              responsiveAnimationDuration: 0, // Disable responsive animation
              scales: {
                  r: {
                      min: 0,
                      max: 100,
                      ticks: {
                          stepSize: 20,
                          callback: function(value, index, values) {
                              if ([20, 40, 60, 80, 100].includes(value)) {
                                  return value;
                              }
                              return null;
                          }
                      }
                  }
              }
          }
      };
  }

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <svg ref={svgRef}></svg>

      {/* Filters Button */}
          <button
            className="filters-button"
            onClick={() => setShowFilters(!showFilters)}
          >
            Filters
          </button>

      {/* Filter Menu Placeholder */}
                {showFilters && (
                  <div className="filter-menu">
                    {/* Close button for the menu */}
                    <button className="filter-menu-close-button" onClick={() => setShowFilters(false)}>
                      &times;
                    </button>
      
                                  {/* Filter Type */}
                                  <div className="filter-section">
                                    <h5>Filter Type</h5>
                                    <label>
                                      <input
                                        type="radio"
                                        value="No Filters"
                                        checked={selectedFilterType === 'No Filters'}
                                        onChange={() => setSelectedFilterType('No Filters')}
                                      />
                                      No Filters
                                    </label>
                                                    <label>
                                                      <input
                                                        type="radio"
                                                        value="Overall Score"
                                                        checked={selectedFilterType === 'Overall Score'}
                                                        onChange={() => setSelectedFilterType('Overall Score')}
                                                      />
                                                      Overall Score
                                                    </label>
                                                    <label>
                                                      <input
                                                        type="radio"
                                                        value="Industry Score"
                                                        checked={selectedFilterType === 'Industry Score'}
                                                        onChange={() => setSelectedFilterType('Industry Score')}
                                                      />
                                                      Industry Score
                                                    </label>
                                                    <label>
                                                      <input
                                                        type="radio"
                                                        value="Pillar Score"
                                                        checked={selectedFilterType === 'Pillar Score'}
                                                        onChange={() => setSelectedFilterType('Pillar Score')}
                                                      />
                                                      Pillar Score
                                                    </label>                                  </div>      
              {/* Industry Selection (conditionally rendered) */}
              {selectedFilterType === 'Industry Score' && (
                <div className="filter-section">
                  <h5>Select Industry</h5>
                  <select
                    value={selectedIndustryFilter || ''}
                    onChange={(e) => setSelectedIndustryFilter(e.target.value)}
                  >
                    <option value="">-- Select an Industry --</option>
                    {INDUSTRIES.map(industry => (
                      <option key={industry} value={industry}>
                        {industry.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Pillar Selection (conditionally rendered) */}
              {selectedFilterType === 'Pillar Score' && (
                <div className="filter-section">
                  <h5>Select Pillar</h5>
                  <select
                    value={selectedPillarFilter || ''}
                    onChange={(e) => setSelectedPillarFilter(e.target.value)}
                  >
                    <option value="">-- Select a Pillar --</option>
                    {PILLARS.map(pillar => (
                      <option key={pillar} value={pillar}>
                        {pillar.charAt(0).toUpperCase() + pillar.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
              )}
      
                    {/* Color Scheme */}
                    <div className="filter-section">
                      <h5>Color Scheme</h5>
                      <label>
                        <input
                          type="radio"
                          value="Green-Yellow-Red"
                          checked={colorScheme === 'Green-Yellow-Red'}
                          onChange={() => setColorScheme('Green-Yellow-Red')}
                        />
                        Green-Yellow-Red
                      </label>
                      {/* Add more color schemes here if needed */}
                    </div>
                  </div>
                )}
      {/* Tooltip element, controlled by D3 */}
      <div ref={tooltipRef} style={{
        position: 'absolute',
        opacity: 0,
        padding: '8px',
        background: 'rgba(0, 0, 0, 0.75)',
        color: 'white',
        borderRadius: '4px',
        pointerEvents: 'none',
        whiteSpace: 'nowrap',
        zIndex: 1000 // Ensure tooltip is on top
      }}></div>

      {selectedCountry && (
        <div className='modal-overlay' style={{ '--header-height': `${headerHeight}px` }} onClick={handleCloseModal}>
          <div className='modal' onClick={(e) => e.stopPropagation()}>
            <button className='modal-close' onClick={handleCloseModal}>&times;</button>
            <div className='modal-header'>
              <h2>{civiData?.name || selectedCountry?.properties?.name}</h2>
            </div>
            <div className='modal-body-content'>
              <div className='modal-inner-content'>
                <div className='tabs'>
                  <button className={`tab-button ${activeTab === 'Overview' ? 'active' : ''}`} onClick={() => setActiveTab('Overview')}>Overview</button>
                  <button className={`tab-button ${activeTab === 'Communications' ? 'active' : ''}`} onClick={() => setActiveTab('Communications')}>Communications</button>
                  <button className={`tab-button ${activeTab === 'Defence' ? 'active' : ''}`} onClick={() => setActiveTab('Defence')}>Defence</button>
                  <button className={`tab-button ${activeTab === 'Energy' ? 'active' : ''}`} onClick={() => setActiveTab('Energy')}>Energy</button>
                  <button className={`tab-button ${activeTab === 'Finance' ? 'active' : ''}`} onClick={() => setActiveTab('Finance')}>Finance</button>
                  <button className={`tab-button ${activeTab === 'Food & Agriculture' ? 'active' : ''}`} onClick={() => setActiveTab('Food & Agriculture')}>Food & Agriculture</button>
                  <button className={`tab-button ${activeTab === 'Healthcare' ? 'active' : ''}`} onClick={() => setActiveTab('Healthcare')}>Healthcare</button>
                  <button className={`tab-button ${activeTab === 'Transport' ? 'active' : ''}`} onClick={() => setActiveTab('Transport')}>Transport</button>
                  <button className={`tab-button ${activeTab === 'Water' ? 'active' : ''}`} onClick={() => setActiveTab('Water')}>Water</button>
                  <button className={`tab-button ${activeTab === 'Waste Management' ? 'active' : ''}`} onClick={() => setActiveTab('Waste Management')}>Waste Management</button>
                  <button className={`tab-button ${activeTab === 'Emergency Services' ? 'active' : ''}`} onClick={() => setActiveTab('Emergency Services')}>Emergency Services</button>
                  <button className={`tab-button ${activeTab === 'Information Technology' ? 'active' : ''}`} onClick={() => setActiveTab('Information Technology')}>Information Technology</button>
                </div>
                <div className='tab-content'>
                  {activeTab === 'Overview' && (() => {
                    const overviewData = getRadarData();
                    return (
                        <div>
            <h3>Overview</h3>
            <p className="radar-chart-explainer">The radar chart visually represents a country's performance across various indicators. Each spoke of the web represents a different indicator, and the distance from the center indicates the country's score for that indicator. A larger area covered by the chart suggests stronger overall performance.</p>
            {/* Radar Chart */}
            <div className="modal-radar-chart">
              {overviewData ? <Radar data={{ labels: overviewData.labels, datasets: overviewData.datasets }} options={overviewData.options} width={400} height={400} /> : <p>No radar chart data available for this country.</p>}
            </div>
                        </div>
                    );
                  })()}
                  {activeTab === 'Communications' && <IndustryRadarChart industryKey="communications" industryName="Communications" civiData={civiData} selectedCountry={selectedCountry} />}
                  {activeTab === 'Defence' && <IndustryRadarChart industryKey="defence" industryName="Defence" civiData={civiData} selectedCountry={selectedCountry} />}
                  {activeTab === 'Energy' && <IndustryRadarChart industryKey="energy" industryName="Energy" civiData={civiData} selectedCountry={selectedCountry} />}
                  {activeTab === 'Finance' && <IndustryRadarChart industryKey="finance" industryName="Finance" civiData={civiData} selectedCountry={selectedCountry} />}
                  {activeTab === 'Food & Agriculture' && <IndustryRadarChart industryKey="food_agriculture" industryName="Food & Agriculture" civiData={civiData} selectedCountry={selectedCountry} />}
                  {activeTab === 'Healthcare' && <IndustryRadarChart industryKey="healthcare" industryName="Healthcare" civiData={civiData} selectedCountry={selectedCountry} />}
                  {activeTab === 'Transport' && <IndustryRadarChart industryKey="transport" industryName="Transport" civiData={civiData} selectedCountry={selectedCountry} />}
                  {activeTab === 'Water' && <IndustryRadarChart industryKey="water" industryName="Water" civiData={civiData} selectedCountry={selectedCountry} />}
                  {activeTab === 'Waste Management' && <IndustryRadarChart industryKey="waste_management" industryName="Waste Management" civiData={civiData} selectedCountry={selectedCountry} />}
                  {activeTab === 'Emergency Services' && <IndustryRadarChart industryKey="emergency_services" industryName="Emergency Services" civiData={civiData} selectedCountry={selectedCountry} />}
                  {activeTab === 'Information Technology' && <IndustryRadarChart industryKey="information_technology" industryName="Information Technology" civiData={civiData} selectedCountry={selectedCountry} />}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExplorePage;
