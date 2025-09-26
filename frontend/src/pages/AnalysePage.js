import React, { useState, useEffect, useCallback } from 'react';
import * as d3 from 'd3'; // Assuming d3 will be used for data fetching
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import './AnalysePage.css';
import { SketchPicker } from 'react-color'; // Import SketchPicker

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// Redefine PILLARS and INDUSTRIES for AnalysePage
const PILLARS = ["autonomy", "resilience", "sustainability", "effectiveness"];
const INDUSTRIES = [
    "communications", "defence", "energy", "finance", "food_agriculture",
    "healthcare", "transport", "water", "waste_management", "emergency_services",
    "information_technology",
];

const HistoricalChart = ({ chartData }) => {
  if (!chartData || chartData.datasets.length === 0) {
    return <p>No data selected for charting. Please add a selection to view the chart.</p>;
  }

  const data = {
    labels: chartData.labels,
    datasets: chartData.datasets,
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false, // Allow chart to fill container
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: 'white', // Legend text color
        },
      },
      title: {
        display: true,
        text: 'Historical Trends',
        color: 'white', // Title text color
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += context.parsed.y.toFixed(2);
            }
            return label;
          }
        }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Year',
          color: 'white', // X-axis title color
        },
        ticks: {
          color: 'white', // X-axis tick color
        },
        grid: {
          color: '#555', // X-axis grid color
        },
      },
      y: {
        title: {
          display: true,
          text: 'Score',
          color: 'white', // Y-axis title color
        },
        min: 0,
        max: 100,
        ticks: {
          color: 'white', // Y-axis tick color
        },
        grid: {
          color: '#555', // Y-axis grid color
        },
      },
    },
  };

  return (
    <div style={{ height: '400px', width: '100%' }}> {/* Set a fixed height for the chart container */}
      <Line data={data} options={options} />
    </div>
  );
};

const AnalysePage = ({ headerHeight }) => {
  const [countryInfoMap, setCountryInfoMap] = useState({});
  const [selections, setSelections] = useState([]);
  const [currentSelection, setCurrentSelection] = useState({ country: '', industry: '', pillar: '', color: '#FF0000' }); // Default to red
  const [timeframe, setTimeframe] = useState({ startYear: 2019, endYear: 2024 });
  const [allHistoricalData, setAllHistoricalData] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredCountries, setFilteredCountries] = useState([]);
  const [displayColorPicker, setDisplayColorPicker] = useState(false); // State for color picker visibility
  const [editingSelectionId, setEditingSelectionId] = useState(null); // State to track which selection's color is being edited

  useEffect(() => {
    d3.json('/country-codes.json')
      .then(codes => {
        const infoMap = codes.reduce((acc, d) => {
          acc[d['alpha-3']] = d;
          return acc;
        }, {});
        setCountryInfoMap(infoMap);
      })
      .catch(error => console.error("Error loading country codes:", error));
  }, []);

  const getCountryDisplayName = useCallback((alpha3) => {
    return countryInfoMap[alpha3]?.name || alpha3;
  }, [countryInfoMap]);

  useEffect(() => {
    if (searchTerm === '') {
      setFilteredCountries([]);
    } else {
      const lowerCaseSearchTerm = searchTerm.toLowerCase();
      const exactMatch = Object.keys(countryInfoMap).some(alpha3 =>
        getCountryDisplayName(alpha3).toLowerCase() === lowerCaseSearchTerm
      );

      if (exactMatch) {
        setFilteredCountries([]);
      } else {
        const results = Object.keys(countryInfoMap).filter(alpha3 =>
          getCountryDisplayName(alpha3).toLowerCase().includes(lowerCaseSearchTerm)
        );
        setFilteredCountries(results);
      }
    }
  }, [searchTerm, countryInfoMap, getCountryDisplayName]);

  const handleAddSelection = () => {
    if (!currentSelection.country) {
      alert("Please select a country.");
      return;
    }

    const newSelection = {
      id: Date.now(),
      ...currentSelection,
    };

    setSelections([...selections, newSelection]);
    setCurrentSelection({ country: '', industry: '', pillar: '', color: '#FF0000' }); // Reset color to default
    setSearchTerm('');
    setDisplayColorPicker(false);
  };

  const handleDeleteSelection = (id) => {
    setSelections(selections.filter(sel => sel.id !== id));
  };

  const getFilteredHistoricalData = useCallback(() => {
    const datasets = selections.map(selection => {
      console.log('selection', selection);
      const countryData = allHistoricalData[selection.country];
      console.log('countryData', countryData);
      if (!countryData) return null;

      const historicalScores = countryData.historical_scores?.map((record, index) => ({
        ...record,
        year: timeframe.startYear + index // Assign year based on index
      }))?.filter(record =>
        record.year >= timeframe.startYear && record.year <= timeframe.endYear
      ) || [];
      console.log('historicalScores', historicalScores);

      const data = historicalScores.map(record => {
        let score = null;

        if (selection.industry && selection.pillar) {
          // Industry and Pillar selected
          score = record.industries?.[selection.industry]?.scores?.[selection.pillar];
        } else if (selection.industry) {
          // Only Industry selected
          const industryScores = record.industries?.[selection.industry]?.scores;
          if (industryScores) {
            const validScores = PILLARS.map(p => industryScores[p]).filter(s => s != null);
            if (validScores.length > 0) {
              score = validScores.reduce((a, b) => a + b, 0) / validScores.length;
            }
          }
        } else if (selection.pillar) {
            // Only Pillar selected
            const pillarScore = record.scores?.[selection.pillar];
            if (pillarScore) {
                score = pillarScore;
            }
        }else {
          // Only Country selected
          const overallScores = record.scores;
          if (overallScores) {
            const validScores = PILLARS.map(p => overallScores[p]).filter(s => s != null);
            if (validScores.length > 0) {
              score = validScores.reduce((a, b) => a + b, 0) / validScores.length;
            }
          }
        }
        return { x: record.year, y: score };
      });

      let label = getCountryDisplayName(selection.country);
      if (selection.industry) label += ` > ${selection.industry.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}`;
      if (selection.pillar) label += ` > ${selection.pillar.charAt(0).toUpperCase() + selection.pillar.slice(1)}`;

      return {
        label,
        data,
        borderColor: selection.color,
        backgroundColor: selection.color,
        fill: false,
        tension: 0.1,
      };
    }).filter(Boolean);

    const labels = Array.from(new Set(datasets.flatMap(ds => ds.data.map(d => d.x)))).sort();

    return {
        labels,
        datasets,
    };

  }, [allHistoricalData, selections, timeframe, getCountryDisplayName]);

  useEffect(() => {
    if (countryInfoMap && Object.keys(countryInfoMap).length > 0) {
      const fetchPromises = Object.values(countryInfoMap).map(info =>
        d3.json(`/civi_modular/${info['alpha-3']}.json`)
          .then(data => ({ [info['alpha-3']]: data }))
          .catch(error => {
            console.error(`Error loading data for ${info['alpha-3']}:`, error);
            return { [info['alpha-3']]: null }; // Return null for failed fetches
          })
      );

      Promise.all(fetchPromises)
        .then(results => {
          const combinedData = results.reduce((acc, curr) => ({ ...acc, ...curr }), {});
          setAllHistoricalData(combinedData);
        });
    }
  }, [countryInfoMap]);

  return (
    <div style={{ paddingTop: `${headerHeight}px`, color: 'white', padding: '20px' }}>
      <h2>Analyse Page</h2>
      <p>This page will provide deeper analysis of each country and their critical industries.</p>

      <div className="analyse-section">
        <h3>Comparison Builder</h3>
        <div>
          <label>Country:</label>
          <input
            type="text"
            className="analyse-input-text"
            placeholder="Search for a country..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <div className="country-search-results">
              {filteredCountries.map(alpha3 => (
                <button
                  key={alpha3}
                  className="country-search-item"
                  onClick={() => {
                    setCurrentSelection({ ...currentSelection, country: alpha3 });
                    setSearchTerm(getCountryDisplayName(alpha3));
                    setFilteredCountries([]);
                  }}
                >
                  {getCountryDisplayName(alpha3)}
                </button>
              ))}
            </div>
          )}
        </div>
        <div>
          <label>Industry:</label>
          <select
            className="analyse-select"
            value={currentSelection.industry}
            onChange={(e) => setCurrentSelection({ ...currentSelection, industry: e.target.value })}
          >
            <option value="">Overall</option>
            {INDUSTRIES.map(industry => (
              <option key={industry} value={industry}>
                {industry.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label>Pillar:</label>
          <select
            className="analyse-select"
            value={currentSelection.pillar}
            onChange={(e) => setCurrentSelection({ ...currentSelection, pillar: e.target.value })}
            disabled={!currentSelection.industry}
          >
            <option value="">Overall</option>
            {PILLARS.map(pillar => (
              <option key={pillar} value={pillar}>
                {pillar.charAt(0).toUpperCase() + pillar.slice(1)}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label>Line Colour:</label>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div
              onClick={() => setDisplayColorPicker(!displayColorPicker)}
              style={{
                width: '36px',
                height: '14px',
                borderRadius: '2px',
                background: currentSelection.color,
                cursor: 'pointer',
                border: '1px solid #fff',
              }}
            />
            <span style={{ marginLeft: '10px' }}>{currentSelection.color}</span>
          </div>
          {displayColorPicker ? (
            <div style={{ position: 'absolute', zIndex: '2' }}>
              <div
                style={{
                  position: 'fixed',
                  top: '0px',
                  right: '0px',
                  bottom: '0px',
                  left: '0px',
                }}
                onClick={() => setDisplayColorPicker(false)}
              />
              <SketchPicker
                color={currentSelection.color}
                onChangeComplete={(color) =>
                  setCurrentSelection({ ...currentSelection, color: color.hex })
                }
              />
            </div>
          ) : null}
        </div>
        <button onClick={handleAddSelection} className="analyse-button">Add to Comparison</button>
      </div>

        <div className="analyse-section">
            <h3>Selections</h3>
            <div className="selections-container">
                {selections.map(selection => (
                    <div key={selection.id} className="selection-card" style={{ borderLeft: `5px solid ${selection.color}` }}>
                        <div style={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
                            <div
                                style={{
                                    width: '20px',
                                    height: '20px',
                                    borderRadius: '3px',
                                    background: selection.color,
                                    cursor: 'pointer',
                                    border: '1px solid #fff',
                                    marginRight: '10px',
                                }}
                                onClick={() => setEditingSelectionId(selection.id)}
                            />
                            <span>
                                {getCountryDisplayName(selection.country)}
                                {selection.industry && ` > ${selection.industry.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}`}
                                {selection.pillar && ` > ${selection.pillar.charAt(0).toUpperCase() + selection.pillar.slice(1)}`}
                            </span>
                        </div>
                        <button onClick={() => handleDeleteSelection(selection.id)}>X</button>
                        {editingSelectionId === selection.id && (
                            <div style={{ position: 'absolute', zIndex: '2', top: '100%', left: '0' }}>
                                <div
                                    style={{
                                        position: 'fixed',
                                        top: '0px',
                                        right: '0px',
                                        bottom: '0px',
                                        left: '0px',
                                    }}
                                    onClick={() => setEditingSelectionId(null)}
                                />
                                <SketchPicker
                                    color={selection.color}
                                    onChangeComplete={(color) => {
                                        setSelections(selections.map(sel =>
                                            sel.id === selection.id ? { ...sel, color: color.hex } : sel
                                        ));
                                    }}
                                />
                                <button onClick={() => setEditingSelectionId(null)} style={{ marginTop: '5px' }}>Save</button>
                                <button onClick={() => setEditingSelectionId(null)} style={{ marginTop: '5px', marginLeft: '5px' }}>X</button>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>

      <div className="analyse-section">
        <h3>Historical Data & Comparison</h3>
        <div style={{ minHeight: '300px' }}>
          <div style={{ height: '400px', width: '100%' }}>
            <HistoricalChart chartData={getFilteredHistoricalData()} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysePage;