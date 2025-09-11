import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';
import { geoOrthographic, geoPath } from 'd3-geo';
import { Radar } from 'react-chartjs-2';
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js';
import './ExplorePage.css';

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

  // Fetch all data sources
  useEffect(() => {
    Promise.all([
      d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json'),
      d3.json('/data/civi.json'),
      d3.json('/data/country-codes.json')
    ]).then(([world, civi, codes]) => {
      setWorldData(topojson.feature(world, world.objects.countries));
      setCiviData(civi.countries);
      const codeMap = codes.reduce((acc, d) => {
        const numericId = parseInt(d['country-code'], 10).toString();
        acc[numericId] = d['alpha-3'];
        return acc;
      }, {});
      setCountryCodeMap(codeMap);
    }).catch(error => console.error("Error loading data:", error));
  }, []);

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
    if (!worldData || !civiData || !countryCodeMap || headerHeight === 0) return; // Wait for headerHeight

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
          return selectedCountry === d ? '#ff9800' : (alpha3 && civiData[alpha3] ? '#ccc' : '#666');
      })
      .attr('stroke', '#1a1a1a')
      .attr('stroke-width', 0.5);

    // Add Interactivity
    countryPaths
      .on('mouseover', (event, d) => {
        if (selectedCountry !== d) d3.select(event.currentTarget).attr('fill', '#ff9800');
        const alpha3 = getAlpha3(d);
        const countryName = (alpha3 && civiData[alpha3]?.name) || d.properties.name || 'N/A';
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
            d3.select(event.currentTarget).attr('fill', alpha3 && civiData[alpha3] ? '#ccc' : '#666');
        }
        tooltip.style('opacity', 0);
      })
      .on('click', (event, d) => {
        const alpha3 = getAlpha3(d);
        if (alpha3 && civiData[alpha3]) {
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
      if (!selectedCountry) return {};
      const alpha3 = countryCodeMap[selectedCountry.id];
      const countryData = civiData[alpha3];
      if (!countryData) return {};

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
          }]
      };
  }

  const getIndustryRadarData = (industryKey) => {
      if (!selectedCountry) return {};
      const alpha3 = countryCodeMap[selectedCountry.id];
      const countryData = civiData[alpha3];
      if (!countryData || !countryData.industries || !countryData.industries[industryKey]) return null; // Return null if data not available

      const industryData = countryData.industries[industryKey];

      return {
          labels: ['Autonomy', 'Resilience', 'Sustainability', 'Effectiveness'],
          datasets: [{
              label: `${countryData.name} - ${industryKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`,
              data: [
                  industryData.scores.autonomy,
                  industryData.scores.resilience,
                  industryData.scores.sustainability,
                  industryData.scores.effectiveness,
              ],
              backgroundColor: 'rgba(0, 150, 136, 0.2)',
              borderColor: 'rgba(0, 150, 136, 1)',
              borderWidth: 1,
          }]
      };
  }

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
              <h2>{civiData[countryCodeMap[selectedCountry.id]].name}</h2>
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
                  {activeTab === 'Overview' && (
                    <div>
                      <h3>Overview</h3>
                      <Radar data={getRadarData()} />
                    </div>
                  )}
                  {activeTab === 'Communications' && (
                    <div>
                      <h3>Communications Details</h3>
                      {getIndustryRadarData('communications') ? <Radar data={getIndustryRadarData('communications')} /> : <p>Data not available for Communications.</p>}
                    </div>
                  )}
                  {activeTab === 'Defence' && (
                    <div>
                      <h3>Defence Details</h3>
                      {getIndustryRadarData('defence') ? <Radar data={getIndustryRadarData('defence')} /> : <p>Data not available for Defence.</p>}
                    </div>
                  )}
                  {activeTab === 'Energy' && (
                    <div>
                      <h3>Energy Details</h3>
                      {getIndustryRadarData('energy') ? <Radar data={getIndustryRadarData('energy')} /> : <p>Data not available for Energy.</p>}
                    </div>
                  )}
                  {activeTab === 'Finance' && (
                    <div>
                      <h3>Finance Details</h3>
                      {getIndustryRadarData('finance') ? <Radar data={getIndustryRadarData('finance')} /> : <p>Data not available for Finance.</p>}
                    </div>
                  )}
                  {activeTab === 'Food & Agriculture' && (
                    <div>
                      <h3>Food & Agriculture Details</h3>
                      {getIndustryRadarData('food_agriculture') ? <Radar data={getIndustryRadarData('food_agriculture')} /> : <p>Data not available for Food & Agriculture.</p>}
                    </div>
                  )}
                  {activeTab === 'Healthcare' && (
                    <div>
                      <h3>Healthcare Details</h3>
                      {getIndustryRadarData('healthcare') ? <Radar data={getIndustryRadarData('healthcare')} /> : <p>Data not available for Healthcare.</p>}
                    </div>
                  )}
                  {activeTab === 'Transport' && (
                    <div>
                      <h3>Transport Details</h3>
                      {getIndustryRadarData('transport') ? <Radar data={getIndustryRadarData('transport')} /> : <p>Data not available for Transport.</p>}
                    </div>
                  )}
                  {activeTab === 'Water' && (
                    <div>
                      <h3>Water Details</h3>
                      {getIndustryRadarData('water') ? <Radar data={getIndustryRadarData('water')} /> : <p>Data not available for Water.</p>}
                    </div>
                  )}
                  {activeTab === 'Waste Management' && (
                    <div>
                      <h3>Waste Management Details</h3>
                      {getIndustryRadarData('waste_management') ? <Radar data={getIndustryRadarData('waste_management')} /> : <p>Data not available for Waste Management.</p>}
                    </div>
                  )}
                  {activeTab === 'Emergency Services' && (
                    <div>
                      <h3>Emergency Services Details</h3>
                      {getIndustryRadarData('emergency_services') ? <Radar data={getIndustryRadarData('emergency_services')} /> : <p>Data not available for Emergency Services.</p>}
                    </div>
                  )}
                  {activeTab === 'Information Technology' && (
                    <div>
                      <h3>Information Technology Details</h3>
                      {getIndustryRadarData('information_technology') ? <Radar data={getIndustryRadarData('information_technology')} /> : <p>Data not available for Information Technology.</p>}
                    </div>
                  )}
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