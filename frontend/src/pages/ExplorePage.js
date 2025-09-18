import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';
import { geoOrthographic, geoPath } from 'd3-geo';
import { Radar } from 'react-chartjs-2';
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js';
import './ExplorePage.css';

const PILLARS = ["autonomy", "resilience", "sustainability", "effectiveness"];

// Register Chart.js components
ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const ExplorePage = ({ headerHeight }) => {
  const svgRef = useRef();
  const tooltipRef = useRef();
  const [worldData, setWorldData] = useState(null);
  const [civiData, setCiviData] = useState(null);
  const [countryCodeMap, setCountryCodeMap] = useState(null);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [activeTab, setActiveTab] = useState('Overview');
  const [windowDimensions, setWindowDimensions] = useState({ width: window.innerWidth, height: window.innerHeight });

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

  // Effect to fetch specific country data when selectedCountry changes
  useEffect(() => {
    if (selectedCountry) {
      const alpha3 = countryCodeMap[selectedCountry.id];
      if (alpha3) {
        d3.json(`/civi_modular/${alpha3}.json`)
          .then(data => {
            setCiviData(data); // civiData now holds only the selected country's data
          })
          .catch(error => console.error(`Error loading data for ${alpha3}:`, error));
      }
    } else {
      setCiviData(null); // Clear civiData when no country is selected
    }
  }, [selectedCountry, countryCodeMap]);

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
          return selectedCountry === d ? '#ff9800' : (civiData ? '#ccc' : '#666');
      })
      .attr('stroke', '#1a1a1a')
      .attr('stroke-width', 0.5);

    // Add Interactivity
    countryPaths
      .on('mouseover', (event, d) => {
        if (selectedCountry !== d) d3.select(event.currentTarget).attr('fill', '#ff9800');
        const alpha3 = getAlpha3(d);
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
        if (selectedCountry !== d) {
            const alpha3 = getAlpha3(d);
            let fillColor = '#666'; // Default color
            if (alpha3 && civiData && civiData[alpha3]) {
                fillColor = '#ccc';
            }
            d3.select(event.currentTarget).attr('fill', fillColor);
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

  }, [worldData, civiData, countryCodeMap, selectedCountry, headerHeight, windowDimensions]); // Added windowDimensions to dependencies

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

  const getIndustryRadarData = (industryKey) => {
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
  }

  const IndustryRadarChart = ({ industryKey, industryName }) => {
    const industryData = getIndustryRadarData(industryKey);
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

    const calculationExplanation = () => {
        if (!pillarScores) return null;

        return (
            <div style={{ marginTop: '20px' }}>
                <h4>Pillar Score Calculation</h4>
                <p>Each pillar score is a weighted average of its underlying indicators.</p>
                <ul>
                    {PILLARS.map(pillar => {
                        const score = pillarScores[pillar];
                        const confidenceScore = pillarScores[`${pillar}_confidence`];

                        const indicatorsForPillar = industryIndicators.filter(i => i.pillar === pillar && i.value !== null);

                        const hasScore = score !== null && score !== undefined;
                        const hasIndicators = indicatorsForPillar.length > 0;

                        let calculation = '';
                        if (hasScore && hasIndicators) {
                            const weightedSum = indicatorsForPillar.reduce((acc, i) => acc + (i.value * i.weight), 0);
                            const totalWeight = indicatorsForPillar.reduce((acc, i) => acc + i.weight, 0);
                            const formula = indicatorsForPillar.map(i => `(${i.value.toFixed(2)} * ${i.weight})`).join(' + ');
                            calculation = `((${formula}) / ${totalWeight.toFixed(2)})`;
                        }

                        return (
                            <li key={pillar}>
                                <strong>{pillar.charAt(0).toUpperCase() + pillar.slice(1)}:</strong>
                                {hasScore ? <span>{` ${score.toFixed(2)}`}</span> : <span> No data</span>}
                                {confidenceScore !== undefined && <span style={{ marginLeft: '10px' }}>(Confidence: {(confidenceScore * 100).toFixed(0)}%)</span>}
                                {calculation && <span> {calculation}</span>}
                            </li>
                        );
                    })}
                </ul>
            </div>
        );
    };

    return (
        <div>
            <h3>{industryName} Details</h3>
            <div className="chart-container">
                {industryData ? <Radar data={industryData} options={industryData.options} plugins={[errorBarsPlugin]} width={400} height={400} /> : <p>Data not available for {industryName}.</p>}
            </div>
            {industryIndicators && (
                <div style={{ marginTop: '20px' }}>
                    <h4>Underlying Indicators</h4>
                    <table className="indicators-table">
                        <thead>
                            <tr>
                                <th>Indicator</th>
                                <th>Value</th>
                                <th>Source</th>
                                <th>Pillar</th>
                            </tr>
                        </thead>
                        <tbody>
                            {industryIndicators.map(indicator => (
                                <tr key={indicator.key}>
                                    <td>{indicator.description}</td>
                                    <td>{indicator.value !== null ? indicator.value.toFixed(2) : 'N/A'}</td>
                                    <td>{indicator.source}{indicator.year ? `, ${indicator.year}` : ''}</td>
                                    <td>{indicator.pillar}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {calculationExplanation()}
                </div>
            )}
        </div>
    );
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <svg ref={svgRef}></svg>

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
                            <div className="chart-container">
                                {overviewData ? <Radar data={overviewData} options={overviewData.options} width={400} height={400} /> : <p>Data not available for Overview.</p>}
                            </div>
                        </div>
                    );
                  })()}
                  {activeTab === 'Communications' && <IndustryRadarChart industryKey="communications" industryName="Communications" />}
                  {activeTab === 'Defence' && <IndustryRadarChart industryKey="defence" industryName="Defence" />}
                  {activeTab === 'Energy' && <IndustryRadarChart industryKey="energy" industryName="Energy" />}
                  {activeTab === 'Finance' && <IndustryRadarChart industryKey="finance" industryName="Finance" />}
                  {activeTab === 'Food & Agriculture' && <IndustryRadarChart industryKey="food_agriculture" industryName="Food & Agriculture" />}
                  {activeTab === 'Healthcare' && <IndustryRadarChart industryKey="healthcare" industryName="Healthcare" />}
                  {activeTab === 'Transport' && <IndustryRadarChart industryKey="transport" industryName="Transport" />}
                  {activeTab === 'Water' && <IndustryRadarChart industryKey="water" industryName="Water" />}
                  {activeTab === 'Waste Management' && <IndustryRadarChart industryKey="waste_management" industryName="Waste Management" />}
                  {activeTab === 'Emergency Services' && <IndustryRadarChart industryKey="emergency_services" industryName="Emergency Services" />}
                  {activeTab === 'Information Technology' && <IndustryRadarChart industryKey="information_technology" industryName="Information Technology" />}
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