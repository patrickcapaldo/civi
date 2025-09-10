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
        <div className='modal-overlay' onClick={handleCloseModal}>
          <div className='modal' onClick={(e) => e.stopPropagation()}>
            <button className='modal-close' onClick={handleCloseModal}>&times;</button>
            <h2>{civiData[countryCodeMap[selectedCountry.id]].name}</h2>
            <div className='modal-content'>
                <Radar data={getRadarData()} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExplorePage;